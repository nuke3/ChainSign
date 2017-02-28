# -* encoding: utf-8 *-
from gui import mainwindow
import sys
from PySide import QtGui, QtCore


class MainWindow(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None, app=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app = app

    @QtCore.Slot()
    def on_verifyButton_clicked(self):
        print('verify')

    @QtCore.Slot()
    def on_timestampButton_clicked(self):
        print('timestamp')

    @QtCore.Slot()
    def on_actionExit_triggered(self):
        """This handles activation of "Exit" menu action"""
        self.app.exit()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app=app)
    window.show()
    sys.exit(app.exec_())
