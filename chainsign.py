# -* encoding: utf-8 *-
import sys
import os
import logging
import traceback
import json

from PySide import QtGui, QtCore

# This is needed for SVG assets to be loaded on Windows builds!
from PySide import QtSvg, QtXml  # noqa

from gui import mainwindow, about

from timestamper import rpcurl_from_config
from workers import VerifyThread, TimestampThread
from models import FileListModel
from updater import UpdateCheckerThread


logging.basicConfig(level=logging.DEBUG)

def qt_excepthook(type, value, tb):
    sys.__excepthook__(type, value, tb)

    msgbox = QtGui.QMessageBox()
    msgbox.setInformativeText("Unexpected error occured")
    msgbox.setText(str(value))
    msgbox.setDetailedText('\n'.join(traceback.format_exception(type, value, tb)))
    msgbox.setIcon(QtGui.QMessageBox.Critical)
    msgbox.exec_()


sys.excepthook = qt_excepthook

def walk(directory):
    """Generator yielding provided directory files recursively"""

    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)

class AboutDialog(QtGui.QDialog, about.Ui_AboutDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        th = UpdateCheckerThread(self)
        th.response.connect(self.on_updater_response)
        th.start()

    def on_updater_response(self, resp):
        data = json.loads(resp)

        if data is None:
            self.updaterLabel.setText("Non-public development release")
        elif data.get('error'):
            self.updaterLabel.setText(
                '<i>An error occured during update check:</i><br />'
                '%s' % data.get('error'))
        elif data.get('binary_url'):
            latest = data.get('latest')
            self.updaterLabel.setText(
                'New update available: <b>%s</b> <i>(%s)</i><br />'
                '<a href="%s">Download update</a> &bull; '
                '<a href="%s">Release info</a>' % (
                    latest.get('tag_name'), latest.get('name'),
                    data.get('binary_url'), latest.get('html_url')))
        else:
            self.updaterLabel.setText("No update available")

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

    @QtCore.Slot()
    def on_actionAbout_triggered(self):
        AboutDialog(self).exec_()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app=app)
    window.show()
    sys.exit(app.exec_())
