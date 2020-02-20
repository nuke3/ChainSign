import logging
import time
from PySide2 import QtCore
from timestamper import NamecoinTimestamper
from utils import rpcurl_from_config
from database import FileEntry


class WorkerThread(QtCore.QThread):
    workFinished = QtCore.Signal([str])
    workFailed = QtCore.Signal([str, str])

    def __init__(self, parent=None, list_model=None):
        super(WorkerThread, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.files = list_model.files

        url = rpcurl_from_config('namecoin', 'http://127.0.0.1:8336/')
        self.timestamper = NamecoinTimestamper(url)

    def run(self):
        failed = False
        for n in self.files:
            try:
                self.process(n)
            except Exception as exc:
                failed = True
                self.logger.exception('Process failed')
                self.workFailed.emit(n.path, 'error: %s' % (exc,))

        if not failed:
            self.workFinished.emit('OK')

    def process(self, f):
        time.sleep(1)
        return 'OK'


class VerifyThread(WorkerThread):
    verifyUpdate = QtCore.Signal([str, str])

    def process(self, f: FileEntry):
        with open(f.path, 'rb') as fd:
            resp = self.timestamper.verify_file(fd)
            if resp and 'timestamp' in resp:
                return 'Found at: %r' % (resp['timestamp'],)
                self.verifyUpdate.emit(f.path, resp)
            else:
                return 'Not found'


class TimestampThread(WorkerThread):
    timestampUpdate = QtCore.Signal([str, str, str, str])

    def process(self, f: FileEntry):
        if not f.can_timestamp:
            return
        with open(f.path, 'rb') as fd:
            reg_txid, nonce, digest = self.timestamper.register_file(fd)
            self.timestampUpdate.emit(f.path, reg_txid, nonce, digest)


class PublishThread(WorkerThread):
    publishUpdate = QtCore.Signal([str, str])

    def process(self, f: FileEntry):
        if not f.can_publish:
            return
        txid = self.timestamper.publish(f.name, f.name_new_nonce, f.name_new_txid)
        if txid:
            self.publishUpdate.emit(f.path, txid)
            return 'Published, transaction ID: %s' % txid
        else:
            return 'Not found'
