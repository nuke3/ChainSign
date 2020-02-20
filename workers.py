import logging
import time
from PySide2 import QtCore
from timestamper import NamecoinTimestamper
from utils import rpcurl_from_config


class WorkerThread(QtCore.QThread):
    workUpdate = QtCore.Signal([str, str])
    workFinished = QtCore.Signal([str])
    workFailed = QtCore.Signal([str])

    def __init__(self, parent=None, list_model=None):
        super(WorkerThread, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.files = list_model.files

        url = rpcurl_from_config('namecoin', 'http://127.0.0.1:8336/')
        self.timestamper = NamecoinTimestamper(url)

    def run(self):
        for n in self.files:
            try:
                self.workUpdate.emit(n[0], self.process(n))
            except Exception as exc:
                self.logger.exception('Process failed')
                self.workUpdate.emit(n[0], 'error: %s' % (exc,))

        self.workFinished.emit('OK')

    def process(self, f):
        time.sleep(1)
        return 'OK'


class VerifyThread(WorkerThread):
    def process(self, f):
        with open(f[0], 'rb') as fd:
            resp = self.timestamper.verify_file(fd)
            if resp and 'timestamp' in resp:
                return 'Found at: %r' % (resp['timestamp'],)
            else:
                return 'Not found'


class TimestampThread(WorkerThread):
    def process(self, f):
        with open(f[0], 'rb') as fd:
            resp = self.timestamper.publish_file(fd)
            if resp:
                return 'Timestamped, transaction ID: %s' % (resp,)
            else:
                return 'Not found'
