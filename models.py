from PySide import QtCore
import operator


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
