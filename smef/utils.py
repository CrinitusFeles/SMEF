import pyqtgraph as pg
import datetime
import time
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen


def timestamp() -> int:
    return round(time.time())


def get_label(probe_id: str) -> str:
    labels: dict[str, str] = {str(key): f'Д{value}' for key, value in zip(range(357217, 3572122), range(1, 6))}
    return labels.get(probe_id, '')


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text="<span style=\"color:black;font-size:20px\">" +
                           'Время' + "</span>", units=None)
        self.enableAutoSIPrefix(False)
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.setTextPen(pen)
        self.setPen(pen)
        font = QtGui.QFont()
        font.setPixelSize(16)
        self.setTickFont(font)

    def tickStrings(self, values, scale, spacing) -> list[str]:
        t_format = "%d.%m.%y\n%H:%M:%S"
        return [datetime.datetime.fromtimestamp(value).strftime(t_format)
                for value in values if value > 100000000]


def open_file_system(directory=False) -> str | None:
    dialog = QtWidgets.QFileDialog()
    print(dialog.directory().absolutePath())
    dialog.setWindowTitle('Choose Directories')
    dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
    if directory:
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
    if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        return dialog.selectedFiles()[0]

    dialog.deleteLater()


if __name__ == '__main__':
    print(round(time.time() * 1000))
