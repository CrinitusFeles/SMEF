import pyqtgraph as pg
import datetime
import time
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
import numpy as np


def create_json_file(config_obj, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as write_file:
            write_file.write(config_obj.to_json())
    except Exception as error:
        print(error)


def timestamp():
    return round(time.time())


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text="<span style=\"color:black;font-size:20px\">" +
                           'Время' + "</span>", units=None)
        self.enableAutoSIPrefix(False)
        self.setTextPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        font = QtGui.QFont()
        font.setPixelSize(16)
        self.setTickFont(font)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%d.%m.%Y\n %H:%M:%S") for value in values if
                value > 100000000]


def converter(value, mode=0):
    """mode = 0 - В/м, mode = 1 В/м -> дБмкВ/м, mode = 2 В/м -> Вт/м2"""
    if mode == 0:
        return value
    elif mode == 1:  # В/м -> дБмкВ/м
        value[value == 0] = 0.001
        return 20 * np.log10(value * 10**6)
    elif mode == 2:  # В/м -> Вт/м2
        return value / 377
    else:
        raise Exception


def reverse_convert(value, mode=1):
    if mode == 1:
        return value * 377
    elif mode == 2:
        return 10 ** (value/20) / 10 ** 6
    else:
        raise Exception

if __name__ == '__main__':
    print(round(time.time() * 1000))
