import pyqtgraph as pg
import datetime
import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen


def timestamp():
    return int(time.mktime(datetime.datetime.now().timetuple()))


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)
        self.setTextPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        font = QtGui.QFont()
        font.setPixelSize(16)
        self.setTickFont(font)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%d.%m.%Y\n %H:%M:%S") for value in values]


