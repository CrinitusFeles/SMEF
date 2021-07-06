import sys
from random import randint

from PyQt5 import QtCore
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
        self.real_time_x_axis_flag = True
        if self.real_time_x_axis_flag:
            pg.PlotWidget.__init__(self, parent=parent, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
            self.setXRange(timestamp() - 50, timestamp() + 50)
            self.x = []  # list(range(100))  # 100 time points
            self.y = [[], [], [], [], []]  # [randint(0, 100) for _ in range(100)]
            
        else:
            pg.PlotWidget.__init__(self, parent=parent)
            self.x = []  # list(range(100))  # 100 time points
            self.y = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]  # [randint(0, 100) for _ in range(100)]
            self.setXRange(- 50, 50)

        self.sensor1 = 0
        self.sensor2 = 0
        self.sensor3 = 0
        self.sensor4 = 0
        self.sensor5 = 0

        self.demonstrate_mode = 1

        self.infinit_line = None

        self.setBackground('#FFFFFF')
        legend = self.addLegend()
        legend.setOffset((500, 10))

        self.showGrid(x=True, y=True)
        self.data_line1 = self.plot(x=self.x, y2=self.y[0], name="Датчик 1",  pen=pg.mkPen(color='g', width=2),
                                    symbol='o', symbolPen='g', symbolSize=2)

        self.data_line2 = self.plot(x=self.x, y=self.y[1], name="Датчик 2", pen=pg.mkPen(color='r', width=2),
                                    symbol='o', symbolPen='r', symbolSize=2)
        self.data_line3 = self.plot(x=self.x, y=self.y[2], name="Датчик 3", pen=pg.mkPen(color='b', width=2),
                                    symbol='o', symbolPen='b', symbolSize=2)
        self.data_line4 = self.plot(x=self.x, y=self.y[3], name="Датчик 4", pen=pg.mkPen(color='y', width=2),
                                    symbol='o', symbolPen='y', symbolSize=2)
        self.data_line5 = self.plot(x=self.x, y=self.y[4], name="Датчик 5", pen=pg.mkPen(color='c', width=2),
                                    symbol='o', symbolPen='y', symbolSize=2)

        self.timer = pg.QtCore.QTimer()
        if not self.real_time_x_axis_flag:
            # self.timer.setInterval(100)
            pass
        else:
            self.timer.setInterval(300)
            self.timer.timeout.connect(self.update_plot_data)
            self.timer.start()

        self.condition = 0
        self.scroll_access = 0

    # def wheelEvent(self, ev):
    #     if self.scroll_access:
    #         super().wheelEvent(ev)

    def update_plot_data(self):
        if self.condition:

            if len(self.x) > 400:
                self.x = self.x[1:]  # Remove the first y element.
                for i in range(len(self.y)):
                    self.y[i] = self.y[i][1:]  # Remove the first
            if self.real_time_x_axis_flag:
                self.x.append(timestamp())
                self.setXRange(timestamp() - 50, timestamp() + 5)
            else:
                self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
                self.setXRange(self.x[-1] - 48, self.x[-1] + 2)

            if self.demonstrate_mode:
                self.y[0].append(randint(0, 100))  # Add a new random value.
                self.data_line1.setData(self.x, self.y[0])  # Update the data.

                # print(np.cos(self.x[-1]))
                self.y[1].append(np.cos(self.x[-1])*20+50)  # Add a new random value.
                self.data_line2.setData(self.x, self.y[1])  # Update the data.

                self.y[2].append(np.sin(self.x[-1])*20+50)  # Add a new random value.
                self.data_line3.setData(self.x, self.y[2])  # Update the data.

                self.y[3].append(np.sin(self.x[-1])*10+200)  # Add a new random value.
                self.data_line4.setData(self.x, self.y[3])  # Update the data.

                self.y[4].append(np.sin(self.x[-1])*2+400)  # Add a new random value.
                self.data_line4.setData(self.x, self.y[4])  # Update the data.

            else:
                self.y[0].append(self.sensor1)
                self.data_line1.setData(self.x, self.y[0])

                self.y[1].append(self.sensor2)
                self.data_line2.setData(self.x, self.y[1])

                self.y[2].append(self.sensor3)
                self.data_line3.setData(self.x, self.y[2])

                self.y[3].append(self.sensor4)
                self.data_line4.setData(self.x, self.y[3])

                self.y[4].append(self.sensor5)
                self.data_line5.setData(self.x, self.y[3])

    def clear_plot(self):
        if self.real_time_x_axis_flag:
            self.setXRange(timestamp() - 50, timestamp() + 50)
            self.x = []  # list(range(100))  # 100 time points
            self.y = [[], [], [], [], []]  # [randint(0, 100) for _ in range(100)]
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