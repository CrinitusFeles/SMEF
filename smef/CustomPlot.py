import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication)
import pyqtgraph as pg
import numpy as np
from .utils import TimeAxisItem, timestamp, converter
from .app_logger import *

logger = get_logger(__name__)


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

        self.sliding_window_size = 3600

        pg.PlotWidget.__init__(self, parent=parent, axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.setXRange(timestamp() - self.sliding_window_size/2, timestamp() + self.sliding_window_size/2)
        self.data = np.array([[], [], [], [], [], []], float)
        self.original_data = np.array([[], [], [], [], [], []], float)

        self.getPlotItem().setLabel('left', "<span style=\"color:black;font-size:20px\">" +
                                    'Амплитуда' + "</span>", units="В/м")
        self.left_axis = self.getPlotItem().getAxis('left')
        self.left_axis.enableAutoSIPrefix(enable=False)
        bottom_axis = self.getPlotItem().getAxis('bottom')

        self.left_axis.setTextPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.left_axis.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        font = QtGui.QFont()
        font.setPixelSize(16)
        # left_axis.setStyle(stopAxisAtTick=(True, True))
        self.left_axis.setTickFont(font)
        # self.left_axis.setLogMode(False)

        self.sensor1 = 0
        self.sensor2 = 0
        self.sensor3 = 0
        self.sensor4 = 0
        self.sensor5 = 0
        self.setLimits(yMin=-10000, yMax=10000, xMin=time.time(), xMax=time.time() + 10000000)

        self.minmax = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ])
        self.demonstrate_mode = 0

        self.infinite_line = None

        # cross hair
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=2))
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g', width=2))
        # self.vb = [None, None, None, None, None]
        self.marker_label = pg.TextItem()
        self.marker_label.setPos(time.time() + 60, 1)
        self.marker_label.setColor('k')
        self.addItem(self.marker_label, ignoreBounds=True)
        self.addItem(self.cursor_vLine, ignoreBounds=True)
        self.addItem(self.cursor_hLine, ignoreBounds=True)
        
        self.display_data_under_mouse = True
        self.freeze_cursor = False

        self.last_mouse_position = None

        self.setBackground('#FFFFFF')
        self.legend = self.addLegend(brush='#08080805', pen='k', colCount=1, labelTextColor='k', labelTextSize='7pt')

        # self.legend.setOffset((700, 10))

        self.showGrid(x=True, y=True)
        self.data_line = [None] * 5

        self.line_colors = ['r', 'g', 'b', 'm', 'c']
        self.line_width = [1, 1, 1, 1, 1]
        self.line_symbol_size = [2, 2, 2, 2, 2]
        self.line_symbol_pen = ['r', 'g', 'b', 'm', 'c']
        self.line_symbol = ['o', 'o', 'o', 'o', 'o']
        for i in range(5):
            self.data_line[i] = self.plot(x=self.data[0], y2=self.data[i+1], name="Датчик " + str(i+1),
                                          pen=({'color': (i, 5), 'width': 1}))

            # print(self.data_line[i])
            # print(self.data_line[i].opts)
        # print(self.legend.items[0][0].item.opts.get('pen'))

        # self.timer = pg.QtCore.QTimer()
        #
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.update_plot_data)
        # self.timer.start()

        self.condition = 0
        self.scroll_access = 0
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

    def init_data(self, sensor_list=None):

        if sensor_list is None:
            sensor_list = [True, True, True, True, True]
        else:
            self.data_line = [None] * 5
            for i in range(5):
                if sensor_list[i]:
                    self.data_line[i] = self.plot(x=self.data[0], y2=self.data[i+1], name="Датчик " + str(i+1),
                                                  pen=({'color': (i, 5), 'width': 1}))

            self.legend.clear()
            for i in range(5):
                if sensor_list[i]:
                    self.legend.addItem(self.data_line[i], "Датчик " + str(i + 1))
            # self.legend.items[i][0].item.opts['pen'] = {'color': (i, 5), 'width': 2}

    def mouse_moved(self, evt):
        if self.display_data_under_mouse and not self.freeze_cursor:
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            self.last_mouse_position = pos
            if self.sceneBoundingRect().contains(pos):
                mouse_point = self.getPlotItem().vb.mapSceneToView(pos)
                marker_text = ''
                for i, data in enumerate(self.data[1:]):
                    # if len(data) > 0:
                    index = np.where(self.data[0].astype(int) == int(mouse_point.x()))[0]
                    if len(index) > 0 and self.data_line[i] is not None:
                        self.marker_label.setFont(QtGui.QFont('Times', 10, QtGui.QFont.Bold))
                        # self.marker_label.setColor(pg.intColor(i))
                        marker_text += 'Д' + str(i + 1) + ': ' + str(data[index[0]]) + ',\n'
                marker_text = marker_text[:-2]
                self.marker_label.setText(marker_text)
                self.marker_label.setPos(mouse_point)

                self.cursor_vLine.setPos(mouse_point.x())
                self.cursor_hLine.setPos(mouse_point.y())

    def wheelEvent(self, ev):
        # if self.scroll_access:
        super().wheelEvent(ev)

    def mousePressEvent(self, ev):
        if ev.buttons() != Qt.MiddleButton:
            super().mousePressEvent(ev)
        else:
            self.freeze_cursor = True

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.freeze_cursor = False

    def update_xrange(self):
        self.setXRange(timestamp() - self.sliding_window_size - 5, timestamp() + 5)

    def update_plot_data(self, mode=0):
        if self.condition:
            if len(self.data[0]) > self.sliding_window_size:
                self.data = np.delete(self.data, 0, axis=1)  # Remove the first
                self.original_data = np.delete(self.original_data, 0, axis=1)

            x_value = timestamp()
            sensor_data = np.array([self.sensor1, self.sensor2, self.sensor3, self.sensor4, self.sensor5]).reshape(5, 1)
            new_data = np.array([x_value, self.sensor1, self.sensor2, self.sensor3, self.sensor4, self.sensor5])
            self.original_data = np.append(self.original_data, np.vstack([[x_value], sensor_data]), axis=1)

            self.data = np.hstack((self.data, np.hstack([new_data[0], converter(new_data[1:], mode=mode)]).reshape(6, 1)))
            for i in range(5):
                if self.data_line[i] is not None:
                    self.data_line[i].setData(self.data[0], self.data[i+1])

            self.minmax = np.row_stack((np.amin(self.data[1:], axis=1), np.mean(self.data[1:], axis=1),
                                        np.amax(self.data[1:], axis=1)))

            self.mouse_moved((self.last_mouse_position, 0))

    def convert_plot_data(self, mode=0):
        copy_array = np.copy(self.original_data)
        self.data[1:, ] = converter(copy_array[1:, ], mode=mode)

    def clear_plot(self):
        self.setXRange(timestamp() - self.sliding_window_size/2, timestamp() + self.sliding_window_size/2)
        self.data = np.array([[], [], [], [], [], []], float)
        self.original_data = np.array([[], [], [], [], [], []], float)
        for i in range(5):
            if self.data_line[i] is not None:
                self.data_line[i].setData(self.data[0], self.data[i+1])

    def start(self):
        self.condition = 1

    def stop(self):
        self.condition = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomPlot()
    window.show()
    sys.exit(app.exec_())
