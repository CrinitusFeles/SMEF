import os
import sys
import time
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication)
import pyqtgraph as pg
import numpy as np
from qtpy.uic import loadUi

from smef.app_logger import get_logger
from smef.utils import TimeAxisItem, timestamp, converter

logger = get_logger(__name__)


class CustomPlot(QWidget):
    def __init__(self, config=None):
        QWidget.__init__(self)
        loadUi(os.path.join(os.path.dirname(__file__), 'custom_plot.ui'), self)
        self.pw = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotter_layout.addWidget(self.pw)
        self.allow_mouse_press = 1
        self.sliding_window_size = 3600

        self.theme = 'light'
        self.palette = None

        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.main_plot_item: pg.PlotItem = self.pw.plotItem
        self.data = np.array([[], [], [], [], [], []], float)
        self.original_data = np.array([[], [], [], [], [], []], float)

        self.current_locale = 'ru'
        self.russian_labels = {'xAxis': 'Время',
                               'yAxis': 'Напряженность',
                               'units': 'В/м',
                               'legend': 'Датчик ',
                               'marker': 'Д'}

        self.english_labels = {'xAxis': 'Time',
                               'yAxis': 'Electric field',
                               'units': 'V/m',
                               'legend': 'Sensor ',
                               'marker': 'S'}

        self.left_axis = self.main_plot_item.getAxis('left')
        self.left_axis.setLabel("<span style=\"color:black;font-size:20px\">" + 'Напряженность' + "</span>", units="В/м")
        self.left_axis.enableAutoSIPrefix(enable=False)
        self.bottom_axis = self.main_plot_item.getAxis('bottom')

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
        self.main_plot_item.setLimits(yMin=-10000, yMax=10000, xMin=timestamp(), xMax=timestamp() + 10000000)

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
        self.pw.addItem(self.marker_label, ignoreBounds=True)
        self.pw.addItem(self.cursor_vLine, ignoreBounds=True)
        self.pw.addItem(self.cursor_hLine, ignoreBounds=True)

        self.display_data_under_mouse = True
        self.freeze_cursor = False

        self.last_mouse_position = None

        self.pw.setBackground('#FFFFFF')
        self.legend = self.main_plot_item.addLegend(brush='#08080805', pen='k', colCount=1, labelTextColor='k', labelTextSize='7pt')
        self.set_theme(self.theme)
        # self.legend.setOffset((700, 10))

        self.pw.showGrid(x=True, y=True)
        self.data_line = [None] * 5

        for i in range(5):
            self.data_line[i] = self.main_plot_item.plot(x=self.data[0], y2=self.data[i + 1],
                                                         name=self.get_label('legend') + str(i + 1),
                                                         pen=({'color': (i, 5), 'width': 1}))

        self.condition = 0
        self.scroll_access = 0
        self.proxy = pg.SignalProxy(self.main_plot_item.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

    def set_theme(self, theme):
        self.theme = theme
        try:
            if theme == 'dark':
                self.palette = {'background': '#121212', 'axis': Qt.white, 'legend_background': '#00000020',
                                'legend_text_color': 'w', 'label_color': '#FFFFFF', 'color': 'white'}
            else:
                self.palette = {'background': '#FFFFFF', 'axis': Qt.black, 'legend_background': '#08080805',
                                'legend_text_color': 'k', 'label_color': '#000000', 'color': 'black'}
                # labelStyle = {'color': '#000000', 'font-size': '12pt'}
            labelStyle = {'color': self.palette.get('label_color'), 'font-size': '12pt'}

            self.left_axis.setTextPen(QPen(self.palette.get('axis'), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.left_axis.setPen(QPen(self.palette.get('axis'), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.left_axis.setLabel(self.get_label('yAxis'), units=self.left_axis.labelUnits, **labelStyle)

            self.bottom_axis.setPen(QPen(self.palette.get('axis'), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.bottom_axis.setTextPen(QPen(self.palette.get('axis'), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.bottom_axis.setLabel(self.get_label('xAxis'), units=self.bottom_axis.labelUnits, **labelStyle)

            self.pw.setBackground(self.palette.get('background'))

            self.legend.setPen(QPen(self.palette.get('axis'), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.legend.setBrush(self.palette.get('legend_background'))
            self.legend.opts['labelTextColor'] = self.palette.get('legend_text_color')
            self.legend.clear()
            if self.current_locale == 'ru':
                labels = self.russian_labels
            else:
                labels = self.english_labels

            for i in range(5):
                if self.data_line[i] is not None:
                    self.legend.addItem(self.data_line[i], labels.get('legend') + str(i + 1))

        except Exception as ex:
            logger.error(ex)

    def init_data(self, sensor_list=None):
        if sensor_list is None:
            sensor_list = [True, True, True, True, True]
        else:
            self.data_line = [None] * 5
            for i in range(5):
                if sensor_list[i]:
                    self.data_line[i] = self.main_plot_item.plot(x=self.data[0], y2=self.data[i + 1],
                                                                 name=self.get_label('legend') + str(i + 1),
                                                                 pen=({'color': (i, 5), 'width': 1}))

            self.legend.clear()
            for i in range(5):
                if sensor_list[i]:
                    self.legend.addItem(self.data_line[i], self.get_label('legend') + str(i + 1))
            # self.legend.items[i][0].item.opts['pen'] = {'color': (i, 5), 'width': 2}

    def mouse_moved(self, evt):
        if self.display_data_under_mouse and not self.freeze_cursor:
            pos = evt[0]  # using signal proxy turns original arguments into a tuple
            self.last_mouse_position = pos
            if self.main_plot_item.vb.sceneBoundingRect().contains(pos):
                mouse_point = self.main_plot_item.vb.mapSceneToView(pos)
                marker_text = ''
                for i, data in enumerate(self.data[1:]):
                    # if len(data) > 0:
                    index = np.where(self.data[0].astype(int) == int(mouse_point.x()))[0]
                    if len(index) > 0 and self.data_line[i] is not None:
                        self.marker_label.setFont(QtGui.QFont('Times', 10, QtGui.QFont.Bold))
                        if self.theme == 'dark':
                            self.marker_label.setColor("#FFFFFF")
                        else:
                            self.marker_label.setColor("#000000")
                        # self.marker_label.setColor(pg.intColor(i))
                        marker_text += self.get_label('marker') + str(i + 1) + ': ' + "{:.2f}".format(
                            data[index[0]]) + '\n'
                marker_text = marker_text[:-1]
                self.marker_label.setText(marker_text)
                self.marker_label.setPos(mouse_point)

                self.cursor_vLine.setPos(mouse_point.x())
                self.cursor_hLine.setPos(mouse_point.y())

    def wheelEvent(self, ev):
        # if self.scroll_access:
        super().wheelEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        super().mouseDoubleClickEvent(ev)
        self.freeze_cursor = not self.freeze_cursor

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

            self.data = np.hstack(
                (self.data, np.hstack([new_data[0], converter(new_data[1:], mode=mode)]).reshape(6, 1)))
            for i in range(5):
                if self.data_line[i] is not None:
                    self.data_line[i].setData(self.data[0], self.data[i + 1])

            self.minmax = np.row_stack((np.amin(self.data[1:], axis=1), np.mean(self.data[1:], axis=1),
                                        np.amax(self.data[1:], axis=1)))

            self.mouse_moved((self.last_mouse_position, 0))

    def convert_plot_data(self, mode=0):
        copy_array = np.copy(self.original_data)
        self.data[1:, ] = converter(copy_array[1:, ], mode=mode)

    def clear_plot(self):
        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.data = np.array([[], [], [], [], [], []], float)
        self.original_data = np.array([[], [], [], [], [], []], float)
        for i in range(5):
            if self.data_line[i] is not None:
                self.data_line[i].setData(self.data[0], self.data[i + 1])

    def start(self):
        self.condition = 1

    def stop(self):
        self.condition = 0

    def change_locale(self, locale='ru'):
        if locale == 'ru':
            labels = self.russian_labels
            self.current_locale = 'ru'
        else:
            labels = self.english_labels
            self.current_locale = 'en'
        self.left_axis.setLabel(labels.get('yAxis'), units=labels.get('units'))
        self.bottom_axis.setLabel(labels.get('xAxis'))
        self.legend.clear()
        for i in range(5):
            if self.data_line[i] is not None:
                self.legend.addItem(self.data_line[i], labels.get('legend') + str(i + 1))

    def get_label(self, key):
        if self.current_locale == 'ru':
            labels = self.russian_labels
        else:
            labels = self.english_labels
        return labels.get(key)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomPlot()
    window.show()
    sys.exit(app.exec_())
