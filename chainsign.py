# -* encoding: utf-8 *-
import sys
import logging
import traceback
import json

from PySide2 import QtCore, QtWidgets

# This is needed for SVG assets to be loaded on Windows builds!
from PySide2 import QtSvg, QtXml  # noqa

from gui import mainwindow, about

from utils import rpcurl_from_config, walk
from workers import VerifyThread, TimestampThread, PublishThread
from models import FileListModel
from updater import UpdateCheckerThread


logging.basicConfig(level=logging.DEBUG)


def qt_excepthook(type, value, tb):
    sys.__excepthook__(type, value, tb)

    msgbox = QtWidgets.QMessageBox()
    msgbox.setInformativeText("Unexpected error occured")
    msgbox.setText(str(value))
    msgbox.setDetailedText('\n'.join(traceback.format_exception(type, value, tb)))
    msgbox.setIcon(QtWidgets.QMessageBox.Critical)
    msgbox.exec_()


sys.excepthook = qt_excepthook


class AboutDialog(QtWidgets.QDialog, about.Ui_AboutDialog):
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


class MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    worker = None

    def __init__(self, parent=None, app=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app

        self.list_model = FileListModel(self)
        self.fileList.setModel(self.list_model)
        self.fileList.resizeColumnsToContents()
        delete_action = QtWidgets.QAction("Delete", self)
        delete_action.triggered.connect(self.on_deleteAction)
        self.fileList.addAction(delete_action)

        if not rpcurl_from_config('namecoin'):
            QtWidgets.QMessageBox.critical(
                self,
                'No namecoind found',
                'Please install and configure Namecoin-Qt first.')
            sys.exit(1)

    def on_deleteAction(self, checked):
        rows = sorted(
            set(idx.row() for idx in self.fileList.selectedIndexes()),
            reverse=True
        )

        for r in rows:
            self.list_model.delete_row(r)
        self.fileList.clearSelection()

    @QtCore.Slot()
    def on_addDirectoryButton_clicked(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self)
        self.add_files(walk(directory))

    @QtCore.Slot()
    def on_addFilesButton_clicked(self):
        files, choice = QtWidgets.QFileDialog.getOpenFileNames(self)
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

    def on_worker_failed(self, fname, status):
        self.list_model.set_status(fname, status)
        self.fileList.resizeColumnsToContents()
        self.statusBar().showMessage("Worker failed: %s: %s" % (fname, status,))

    def on_timestamp_update(self, fname, reg_txid, nonce, digest):
        self.list_model.set_registered(fname, reg_txid, nonce, digest)
        self.fileList.resizeColumnsToContents()

    def on_publish_update(self, fname, txid):
        self.list_model.set_published(fname, txid)
        self.fileList.resizeColumnsToContents()

    def on_verify_update(self, fname, status):
        self.list_model.set_status(fname, status)
        self.fileList.resizeColumnsToContents()

    # Button slots
    #
    @QtCore.Slot()
    def on_verifyButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = VerifyThread(self, self.list_model)
        self.worker.verifyUpdate.connect(self.on_verify_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

    @QtCore.Slot()
    def on_timestampButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return

        self.worker = TimestampThread(self, self.list_model)
        self.worker.timestampUpdate.connect(self.on_timestamp_update)
        self.worker.workFailed.connect(self.on_worker_failed)
        self.worker.workFinished.connect(self.on_worker_finished)
        self.worker.start()

    @QtCore.Slot()
    def on_publishButton_clicked(self):
        if self.processing:
            self.statusBar().showMessage('Work in progress...')
            return
        self.worker = PublishThread(self, self.list_model)
        self.worker.publishUpdate.connect(self.on_publish_update)
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app=app)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
