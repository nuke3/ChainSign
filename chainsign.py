# -* encoding: utf-8 *-
import sys
import os
import logging
import time

from PySide import QtGui, QtCore
from gui import mainwindow

logging.basicConfig(level=logging.DEBUG)


class WorkerThread(QtCore.QThread):
    workUpdate = QtCore.Signal([str, str])
    workFinished = QtCore.Signal([str])
    workFailed = QtCore.Signal([str])

    def __init__(self, parent=None, data=[]):
        super(WorkerThread, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data = data

    def run(self):
        try:
            for n in self.data:
                try:
                    self.workUpdate.emit(str(n), self.process(n))
                except Exception as exc:
                    self.logger.exception('Process failed')
                    self.workFailed.emit(str(exc))

            self.workFinished.emit('OK')
        except Exception as exc:
            self.logger.exception('Run failed')
            self.workFailed.emit(str(exc))

    def process(self):
        time.sleep(1)
        return 'OK'


class VerifyThread(WorkerThread):
    def process(self, filename):
        # TODO
        time.sleep(1)
        return 'OK'


class TimestampThread(WorkerThread):
    def process(self, filename):
        # TODO
        time.sleep(1)
        return 'OK'


def walk(directory):
    """Generator yielding provided directory files recursively"""

    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)


class MainWindow(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    worker = None

    def __init__(self, parent=None, app=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app

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
            files_added += 1

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

    #
    # Button slots
    #
    @QtCore.Slot()
    def on_verifyButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = VerifyThread(self, range(10))
        self.worker.workUpdate.connect(self.on_worker_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

        print('verify')

    @QtCore.Slot()
    def on_timestampButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = TimestampThread(self, range(10))
        self.worker.workUpdate.connect(self.on_worker_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

        print('publish')

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
