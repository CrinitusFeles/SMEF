import sys
from random import randint
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication)
import pyqtgraph as pg
from pyqtgraph import InfiniteLine
import numpy as np
from utils import TimeAxisItem, timestamp


class CustomPlot(QWidget):
    # clicked = pyqtSignal(QWidget)
    def __init__(self, *args):
        QWidget.__init__(self)
        self.layout = QVBoxLayout(self)
        self.pgcustom = CustomPlotWidget(self)
        self.setMinimumHeight(300)
        self.layout.addWidget(self.pgcustom)
        self.allow_mouse_press = 1


class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):

        self.sliding_window_size = 60

        pg.PlotWidget.__init__(self, parent=parent, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.setXRange(timestamp() - self.sliding_window_size/2, timestamp() + self.sliding_window_size/2)
        self.data = np.array([[], [], [], [], [], []])

        self.getPlotItem().setLabel('left', "<span style=\"color:black;font-size:20px\">" +
                               'Амплитуда' + "</span>", units="В/м")
        self.getPlotItem().getAxis('left').setTextPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.getPlotItem().getAxis('left').setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        font = QtGui.QFont()
        font.setPixelSize(16)
        self.getPlotItem().getAxis('left').setTickFont(font)
        self.getPlotItem().getAxis('left').setLogMode(True)

        self.sensor1 = 0
        self.sensor2 = 0
        self.sensor3 = 0
        self.sensor4 = 0
        self.sensor5 = 0

        self.minmax = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ])

        self.demonstrate_mode = 1

        self.infinit_line = None

        self.setBackground('#FFFFFF')
        legend = self.addLegend()
        legend.setOffset((500, 10))

        self.showGrid(x=True, y=True)
        self.data_line1 = self.plot(x=self.data[0], y2=self.data[1], name="Датчик 1",  pen=pg.mkPen(color='g', width=2),
                                    symbol='o', symbolPen='g', symbolSize=2)

        self.data_line2 = self.plot(x=self.data[0], y=self.data[2], name="Датчик 2", pen=pg.mkPen(color='r', width=2),
                                    symbol='o', symbolPen='r', symbolSize=2)
        self.data_line3 = self.plot(x=self.data[0], y=self.data[3], name="Датчик 3", pen=pg.mkPen(color='b', width=2),
                                    symbol='o', symbolPen='b', symbolSize=2)
        self.data_line4 = self.plot(x=self.data[0], y=self.data[4], name="Датчик 4", pen=pg.mkPen(color='y', width=2),
                                    symbol='o', symbolPen='y', symbolSize=2)
        self.data_line5 = self.plot(x=self.data[0], y=self.data[5], name="Датчик 5", pen=pg.mkPen(color='c', width=2),
                                    symbol='o', symbolPen='y', symbolSize=2)

        self.timer = pg.QtCore.QTimer()

        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.condition = 0
        self.scroll_access = 0

    def wheelEvent(self, ev):
        # if self.scroll_access:
        super().wheelEvent(ev)

    def update_xrange(self):
        self.setXRange(timestamp() - self.sliding_window_size - 5, timestamp() + 5)

    def update_plot_data(self):
        if self.condition:
            if len(self.data[0]) > self.sliding_window_size:
                self.data = np.delete(self.data, 0, axis=1)  # Remove the first

            x_value = timestamp()
            measure1 = randint(0, 100)
            measure2 = np.cos(x_value)*20+50
            measure3 = np.sin(x_value)*20+50
            measure4 = np.sin(x_value)*10+200
            measure5 = np.sin(x_value)*2+400

            if self.demonstrate_mode:

                for i in np.nditer(self.minmax.reshape(1, 15)):
                    pass

                new_data = np.array([x_value, measure1, measure2, measure3, measure4, measure5]).reshape(6, 1)
                self.data = np.hstack((self.data, new_data))
                self.data_line1.setData(self.data[0], self.data[1])  # Update the data.
                self.data_line2.setData(self.data[0], self.data[2])  # Update the data.
                self.data_line3.setData(self.data[0], self.data[3])  # Update the data.
                self.data_line4.setData(self.data[0], self.data[4])  # Update the data.
                self.data_line4.setData(self.data[0], self.data[5])  # Update the data.


            else:
                self.y[0] = np.append(self.y[0], self.sensor1)
                self.data_line1.setData(self.x, self.y[0])

                self.y[1] = np.append(self.y[1], self.sensor2)
                self.data_line2.setData(self.x, self.y[1])

                self.y[2] = np.append(self.y[2], self.sensor3)
                self.data_line3.setData(self.x, self.y[2])

                self.y[3] = np.append(self.y[3], self.sensor4)
                self.data_line4.setData(self.x, self.y[3])

                self.y[4] = np.append(self.y[4], self.sensor5)
                self.data_line5.setData(self.x, self.y[3])

    def clear_plot(self):
        if self.real_time_x_axis_flag:
            self.setXRange(timestamp() - 50, timestamp() + 50)
            self.x = np.array([], int)  # list(range(100))  # 100 time points
            self.y = np.array([[], [], [], [], []])  # [randint(0, 100) for _ in range(100)]
        else:
            self.setXRange(self.x[-1] - 48, self.x[-1] + 2)
            self.x = [0, 0]  # list(range(100))  # 100 time points
            self.y = [[0, 0], [0, 0], [0, 0], [0, 0]]  # [randint(0, 100) for _ in range(100)]
        self.data_line1.setData(self.x, self.y[0])
        self.data_line2.setData(self.x, self.y[1])
        self.data_line3.setData(self.x, self.y[2])
        self.data_line4.setData(self.x, self.y[3])
        self.data_line5.setData(self.x, self.y[4])

    def start(self):
        self.condition = 1

    def stop(self):
        self.condition = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomPlot()
    window.show()
    sys.exit(app.exec_())