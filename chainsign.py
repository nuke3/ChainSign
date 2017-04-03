# -* encoding: utf-8 *-
import sys
import os
import logging
import time
import operator
import traceback

from PySide import QtGui, QtCore
from gui import mainwindow

from timestamper import rpcurl_from_config, NamecoinTimestamper

logging.basicConfig(level=logging.DEBUG)


def qt_excepthook(type, value, tb):
    sys.__excepthook__(type, value, tb)

    msgbox = QtGui.QMessageBox()
    msgbox.setText("Unexpected error occured")
    msgbox.setInformativeText(str(value))
    msgbox.setDetailedText('\n'.join(traceback.format_exception(type, value, tb)))
    msgbox.setIcon(QtGui.QMessageBox.Critical)
    msgbox.exec_()


sys.excepthook = qt_excepthook

class WorkerThread(QtCore.QThread):
    workUpdate = QtCore.Signal([str, str])
    workFinished = QtCore.Signal([str])
    workFailed = QtCore.Signal([str])

    def __init__(self, parent=None, list_model=None):
        super(WorkerThread, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.list_model = list_model

        url = rpcurl_from_config('namecoin', 'http://127.0.0.1:8336/')
        self.timestamper = NamecoinTimestamper(url)

    def run(self):
        try:
            for n in self.list_model.files:
                try:
                    self.workUpdate.emit(n[0], self.process(n))
                except Exception as exc:
                    self.logger.exception('Process failed')
                    self.workUpdate.emit(n[0], 'error: %s' % (exc,))

            self.workFinished.emit('OK')
        except Exception as exc:
            self.logger.exception('Run failed')
            self.workFailed.emit(str(exc))

    def process(self):
        time.sleep(1)
        return 'OK'


class VerifyThread(WorkerThread):
    def process(self, f):
        with open(f[0], 'r') as fd:
            resp = self.timestamper.verify_file(fd)
            if resp and 'timestamp' in resp:
                return 'Found at: %r' % (resp['timestamp'],)
            else:
                return 'Not found'


class TimestampThread(WorkerThread):
    def process(self, f):
        with open(f[0], 'r') as fd:
            resp = self.timestamper.publish_file(fd)
            if resp:
                return 'Timestamped, transaction ID: %s' % (resp,)
            else:
                return 'Not found'


def walk(directory):
    """Generator yielding provided directory files recursively"""

    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)


class FileListModel(QtCore.QAbstractTableModel):
    headers = ['File', 'Status']

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)
        self.files = []

    def rowCount(self, parent):
        return len(self.files)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.files[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headers[col]
        return None

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        self.files = sorted(self.files, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.files.reverse()
        self.layoutChanged.emit()

    def add_file(self, fname):
        self.layoutAboutToBeChanged.emit()
        self.files.append([fname, 'pending'])
        self.layoutChanged.emit()

    def update_file(self, fname, status):
        self.layoutAboutToBeChanged.emit()
        for f in self.files:
            # FIXME
            if f[0] == fname:
                f[1] = status
        self.layoutChanged.emit()


class MainWindow(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    worker = None

    def __init__(self, parent=None, app=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app

        self.list_model = FileListModel(self)
        self.fileList.setModel(self.list_model)

        if not rpcurl_from_config('namecoin'):
            QtGui.QMessageBox.critical(self,
                    'No namecoind found',
                    'Please install and configure Namecoin-Qt first.')
            sys.exit(1)

    @QtCore.Slot()
    def on_addDirectoryButton_clicked(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self)
        self.add_files(walk(directory))

    @QtCore.Slot()
    def on_addFilesButton_clicked(self):
        files, choice = QtGui.QFileDialog.getOpenFileNames(self)
        self.add_files(files)

    def add_files(self, files_iter):
        """Adds files from iterator to current work queue"""

        files_added = 0

        for f in files_iter:
            # TODO
            self.list_model.add_file(f)
            files_added += 1

        self.fileList.resizeColumnsToContents()
        self.statusBar().showMessage("%d files added." % (files_added,))

    @property
    def processing(self):
        return self.worker and self.worker.isRunning()

    def on_worker_finished(self, status):
        self.statusBar().showMessage("Worker finished: %s" % (status,))

    def on_worker_failed(self, status):
        self.statusBar().showMessage("Worker failed: %s" % (status,))

    def on_worker_update(self, fname, status):
        self.statusBar().showMessage("%s: %s" % (fname, status))
        self.list_model.update_file(fname, status)
        self.fileList.resizeColumnsToContents()

    #
    # Button slots
    #
    @QtCore.Slot()
    def on_verifyButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = VerifyThread(self, self.list_model)
        self.worker.workUpdate.connect(self.on_worker_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

    @QtCore.Slot()
    def on_timestampButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = TimestampThread(self, self.list_model)
        self.worker.workUpdate.connect(self.on_worker_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

    #
    # Main menu slots
    #
    @QtCore.Slot()
    def on_actionQuit_triggered(self):
        """This handles activation of "Exit" menu action"""
        self.app.exit()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app=app)
    window.show()
    sys.exit(app.exec_())
