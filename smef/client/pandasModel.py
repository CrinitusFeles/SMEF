import sys
import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QTableView
from PyQt6.QtCore import pyqtProperty  #type: ignore



class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.ItemDataRole.UserRole + 1000
    ValueRole = QtCore.Qt.ItemDataRole.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._df = df


    @pyqtProperty(pd.DataFrame)
    def df(self):
        return self._df

    @df.setter
    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._df = dataframe.copy()
        self.endResetModel()
    # dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._df.columns[section]
            else:
                return str(self._df.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._df.columns.size

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        dt = self._df[col].dtype

        val = self._df.loc[row][col]
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return str(f'{val:.2f}')
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.ItemDataRole.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


if __name__ == '__main__':

    df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                    'b': [100, 200, 300],
                    'c': ['a', 'b', 'c']})
    app = QApplication(sys.argv)
    model = DataFrameModel(df)
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec())