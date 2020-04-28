from PySide2 import QtCore
import operator
from database import file_database


class FileListModel(QtCore.QAbstractTableModel):
    headers = ['File', 'Status']

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)

    def rowCount(self, parent):
        return len(file_database)

    @property
    def files(self):
        return file_database

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
        if order == QtCore.Qt.DescendingOrder:
            self.files.reverse()
        self.layoutChanged.emit()

    def add_file(self, fname, status="pending"):
        self.layoutAboutToBeChanged.emit()
        file_database.add_file(fname, status)
        self.layoutChanged.emit()

    def delete_row(self, row):
        file_database.del_row(row)

    def set_status(self, fname, status):
        self.layoutAboutToBeChanged.emit()
        file_database.set_status(fname, status)
        self.layoutChanged.emit()

    def set_registered(self, fname, txid, nonce, digest):
        self.layoutAboutToBeChanged.emit()
        file_database.set_file_registered(fname, txid, nonce, digest)
        self.layoutChanged.emit()

    def set_published(self, fname, txid):
        self.layoutAboutToBeChanged.emit()
        file_database.set_file_published(fname, txid)
        self.layoutChanged.emit()
