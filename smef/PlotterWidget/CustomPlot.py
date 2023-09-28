from __future__ import annotations
import datetime
import time
from os import path

import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
from typing import Type, Optional, Literal, Tuple, Any

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QUrl, QMimeData, Qt, QEvent, QPoint, QPointF
from PyQt5.QtGui import QColor, QFont, QPen, QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication
import numpy as np
from numpy import ndarray
from pyqtgraph import InfiniteLine
from qtpy.uic import loadUi

from smef.utils import converter


def timestamp():
    return float(time.time())


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text="<span style=\"color:black;font-size:20px\">" +
                           'Время' + "</span>", units=None)
        self.enableAutoSIPrefix(False)
        self.setTextPen(
            QPen(QColor(kwargs.get('tick_colors', 'k')), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))  # tick values
        self.setPen(QPen(QColor(kwargs.get('grid_colors', 'k')), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))  # grid
        font = QtGui.QFont()
        font.setPixelSize(14)
        self.setTickFont(font)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%H:%M:%S\n%d.%m.%Y") for value in values if
                value > 100000000]


class CustomPlot(QWidget):
    def __init__(self, config: dict):
        QWidget.__init__(self)
        loadUi(path.join(path.dirname(__file__), 'plotter_widget.ui'), self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.config = config
        self.start_button.pressed.connect(self.start_plot)
        self.clear_button.pressed.connect(self.clear_plot)
        self.start_button.hide()
        self.clear_button.hide()
        self.pw = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.pw = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom', tick_colors=
        self.config['style'][self.config['theme']]['axis_labels_color'])})
        self.plot_layout.addWidget(self.pw)

        self.main_plot_item: pg.PlotItem = self.pw.plotItem
        self.main_plot_item.autoBtn.clicked.connect(self.auto_scale)

        self.left_axis = self.main_plot_item.getAxis('left')
        self.right_axis = self.main_plot_item.getAxis('right')
        self.top_axis = self.main_plot_item.getAxis('top')
        self.bottom_axis = self.main_plot_item.getAxis('bottom')
        self.main_plot_item.setLimits(yMin=-10000, yMax=10000, xMin=timestamp(), xMax=timestamp() + 10000000)

        self.right_axis_view_box: Optional[pg.ViewBox] = pg.ViewBox() if config['right_axis'] is not None else None
        if self.right_axis_view_box is not None:
            self.init_extra_axis()

        self.legend = None
        self.set_theme(self.config)

        # time, y1_1, y1_2, y2_1, y2_2
        self.data = np.array([[]], float)
        self.transformed_data = np.array([[]], float)  # array for unit transformation

        self.new_data: list[float] = []

        self.sliding_window_size = 300
        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.data_line: list[Type[pg.PlotDataItem]] = []

        self.plotter_update_timer = QTimer()
        self.plotter_update_timer.timeout.connect(self.__plot_process)
        self.plotter_update_timer.start(config['anim_period'])
        self._plot_process_flag = False
        self.demo_mode = False
        self.auto_scale()
        # self.add_infinite_lines(y1=27, y2=100, color1='r', color2='b')
        self.trace_counter = 0
        self.trace_names = []

        # cross hair
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False,
                                            pen=pg.mkPen(self.config['style'][self.config['theme']]['crosshair_color'],
                                                         width=2))
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False,
                                            pen=pg.mkPen(self.config['style'][self.config['theme']]['crosshair_color'],
                                                         width=2))
        # self.vb = [None, None, None, None, None]
        self.marker_label = pg.TextItem()
        self.marker_label.setPos(time.time() + 60, 1)
        self.marker_label.setColor('k')
        self.pw.addItem(self.marker_label, ignoreBounds=True)
        self.pw.addItem(self.cursor_vLine, ignoreBounds=True)
        self.pw.addItem(self.cursor_hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.main_plot_item.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.display_data_under_mouse = True
        self.freeze_cursor = False

        self.last_mouse_position = None

        self.infinite_line = None

    def set_theme(self, config: dict):
        self.config = config
        self.set_background(plot_color=self.config['style'][self.config['theme']]['plot_background_color'],
                            axes_color=self.config['style'][self.config['theme']]['frame_background_color'])
        self.set_axes_labels(x_label=config['bottom_axis']['label'],
                             y_labels=[f"{self.config['left_axis']['label']}, {self.config['units']}",
                                       f"{self.config['right_axis']['label']}, {self.config['units']}"
                                       if self.config['right_axis'] is not None else None],
                             color=self.config['style'][self.config['theme']]['axis_labels_color'],
                             units=[self.config['left_axis']['units'], None])
        if self.legend is None:
            self.legend = self.main_plot_item.addLegend(
                brush=self.config['style'][self.config['theme']]['legend_background'],
                pen=self.config['style'][self.config['theme']]['legend_boundary'],
                colCount=1,
                labelTextColor=self.config['style'][self.config['theme']]['axis_labels_color'],
                labelTextSize='7pt')
        else:
            self.legend.setPen(self.config['style'][self.config['theme']]['legend_boundary'])
            self.legend.setBrush(self.config['style'][self.config['theme']]['legend_background'])
            self.legend.setLabelTextColor(self.config['style'][self.config['theme']]['axis_labels_color'])

    def set_title(self, title: str):
        self.main_plot_item.setTitle(f"<span style=\"color:"
                                     f"{self.config['style'][self.config['theme']]['axis_labels_color']};"
                                     f"font-size:30px\">{title}</span>")

    def auto_scale(self):
        # self.right_axis_view_box.setYRange()
        self.main_plot_item.enableAutoRange(axis='y')
        if self.right_axis_view_box is not None:
            self.right_axis_view_box.enableAutoRange(axis='y')

    def disable_autoscale(self):
        self.main_plot_item.disableAutoRange(axis='y')
        self.right_axis_view_box.disableAutoRange(axis='y')

    def add_trace(self, name: str, y_axis: Literal['left', 'right']):
        self.data = np.append(self.data, [[]], axis=0)
        self.new_data += [0]
        self.trace_names.append(name)
        self.data_line.append(self.main_plot_item.plot(x=self.data[self.trace_counter],
                                                       y2=self.data[self.trace_counter + 1],
                                                       name=name,
                                                       pen=({'color': (self.trace_counter, self.trace_counter + 2),
                                                             'width': 2})))
        if y_axis == 'right' and self.right_axis_view_box is not None:
            self.right_axis_view_box.addItem(self.data_line[-1])

        self.trace_counter += 1

    def start_plot(self) -> None:
        if self.start_button.text() == 'Начать':
            self.start_button.setText('Остановить')
            self._plot_process_flag = True
        else:
            self._plot_process_flag = False
            self.start_button.setText('Начать')

    def __plot_process(self) -> None:
        if self._plot_process_flag:
            if self.demo_mode:
                self.add_points(
                    [np.sin(timestamp()), np.cos(timestamp()), np.sin(timestamp()) + 5, np.cos(timestamp() * 5) - 10])
            else:
                try:
                    self.add_points(self.new_data)
                except ValueError as err:
                    data = self.data
                    print(data)
                    print(err)

    def init_extra_axis(self) -> None:
        self.main_plot_item.scene().addItem(self.right_axis_view_box)
        self.right_axis_view_box.setGeometry(self.main_plot_item.vb.sceneBoundingRect())
        self.right_axis_view_box.setXLink(self.main_plot_item)
        self.right_axis_view_box.sigYRangeChanged.connect(self.disable_autoscale)
        self.main_plot_item.vb.sigResized.connect(self.update_views)
        self.right_axis.linkToView(self.right_axis_view_box)
        self.main_plot_item.showAxis('right')
        # self.p1.showAxis('top')

    def set_background(self, plot_color: str | QColor, axes_color: str | QColor) -> None:
        if self.right_axis_view_box is not None:
            self.right_axis_view_box.setBackgroundColor(plot_color)
        else:
            v1 = self.main_plot_item.getViewBox()
            v1.setBackgroundColor(plot_color)
        self.pw.setBackground(axes_color)
        self.pw.showGrid(x=True, y=True)

    def set_axes_labels(self, x_label: str, y_labels: list[str], color: str, font_size: int = 16, units=None) -> None:
        font = QFont()
        font.setPixelSize(font_size)
        self.bottom_axis.setLabel(f"<span style=\"font-size:20px;color:{color};\">{x_label}</span>")
        self.bottom_axis.setTickFont(font)

        self.left_axis.setLabel(f"<span style=\"font-size:20px;color:{color};\">{y_labels[0]}</span>", units=units[0])
        self.left_axis.setTickFont(font)
        if self.right_axis_view_box is not None:
            self.right_axis.setLabel(f"<span style=\"font-size:20px;color:{color};\">{y_labels[1]}</span>",
                                     units=units[1])
            self.right_axis.setTickFont(font)

    def add_infinite_lines(self, y1: int, y2: int, color1: str, color2: str, size1: int = 2, size2: int = 2) -> None:
        if self.right_axis_view_box is not None:
            self.right_axis_view_box.addItem(pg.InfiniteLine(angle=0, pos=y1, movable=True,
                                                             pen=pg.mkPen(color2, width=size1)))
        self.main_plot_item.addLine(movable=True, x=None, y=y2, pen=pg.mkPen(color1, width=size2),
                                    label='                                                     '
                                          '                                                 norma')

    def update_views(self) -> None:
        if self.right_axis_view_box is not None:
            self.right_axis_view_box.setGeometry(self.main_plot_item.vb.sceneBoundingRect())

    def add_points(self, data: list[float], units_mode=0) -> None:
        point_count = len(self.data[0])
        if point_count > self.sliding_window_size:
            self.data = np.delete(self.data, 0, axis=1)  # Remove the first
        buf = np.array([timestamp(), *converter(data, mode=units_mode)]).reshape(len(data) + 1, 1)
        self.data = np.hstack((self.data, buf))
        [line.setData(self.data[0], self.data[i + 1]) for i, line in enumerate(self.data_line)]
        # self.mouse_moved((self.last_mouse_position, 0))
        # self.update_views()
        self.main_plot_item.scene().sigMouseMoved.emit(self.last_mouse_position)

    def clear_plot(self) -> None:
        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.data = np.array([[]], float)
        self.new_data = []
        self.data_line = []
        self.trace_names = []
        self.main_plot_item.clear()
        self.pw.addItem(self.marker_label, ignoreBounds=True)
        self.pw.addItem(self.cursor_vLine, ignoreBounds=True)
        self.pw.addItem(self.cursor_hLine, ignoreBounds=True)
        self.legend.clear()
        self.trace_counter = 0
        [line.setData(self.data[0], self.data[i + 1]) for i, line in enumerate(self.data_line)]

    def get_visible_time_interval(self) -> tuple[tuple[float, float], tuple[float, float]]:
        x1_timestamp = self.pw.visibleRange().getCoords()[0]
        x2_timestamp = self.pw.visibleRange().getCoords()[2]
        idx_start = (np.abs(self.data[0] - x1_timestamp)).argmin()
        idx_stop = (np.abs(self.data[0] - x2_timestamp)).argmin()
        return (self.data[0][idx_start], self.data[0][idx_stop]), (idx_start, idx_stop)

    def copy_image(self, folder_path: str) -> Optional[QMimeData]:
        try:
            file_name = datetime.datetime.now().strftime("/%d.%m.%y-%H_%M_%S") + ".png"
            exporter = pg.exporters.ImageExporter(self.main_plot_item)
            data = QtCore.QMimeData()
            url = QtCore.QUrl.fromLocalFile(folder_path + file_name)
            data.setUrls([url])
            exporter.export(folder_path + file_name)
            return data
        except Exception as ex:
            print(ex)

    def mouse_moved(self, evt):
        pos: QPointF = evt[0]  # using signal proxy turns original arguments into a tuple
        self.last_mouse_position = pos
        if self.display_data_under_mouse and not self.freeze_cursor:
            if self.main_plot_item.vb.sceneBoundingRect().contains(pos):
                mouse_point = self.main_plot_item.vb.mapSceneToView(pos)
                marker_text = ''
                self.marker_label.setFont(QtGui.QFont('Times', 10, QtGui.QFont.Bold))
                if self.config['theme'] == 'dark':
                    self.marker_label.setColor("#FFFFFF")
                else:
                    self.marker_label.setColor("#000000")
                for data, name in zip(self.data[1:], self.trace_names):
                    # if len(data) > 0:
                    if len(self.data[0]) > 0:
                        # index = np.where(self.data[0].astype(int) == int(mouse_point.x()))[0]
                        time_array = self.data[0]
                        diff = np.abs(time_array - mouse_point.x())
                        index = diff.argmin()
                        if np.abs(self.data[0][index] - mouse_point.x()) > 1:
                            index = None
                        if index is not None:
                            marker_text += f'Д{name[-8]}: {data[index]:.2f}\n'
                marker_text = marker_text[:-1]
                self.marker_label.setText(marker_text)
                self.marker_label.setPos(mouse_point)

                self.cursor_vLine.setPos(mouse_point.x())
                self.cursor_hLine.setPos(mouse_point.y())

    def mouseDoubleClickEvent(self, ev):
        super().mouseDoubleClickEvent(ev)
        self.freeze_cursor = not self.freeze_cursor
        self.main_plot_item.scene().sigMouseMoved.emit(self.last_mouse_position)

    def set_markers_visible_state(self, state: bool) -> None:
        self.display_data_under_mouse = state
        self.marker_label.setVisible(state)
        self.cursor_vLine.setVisible(state)
        self.cursor_hLine.setVisible(state)

    def norma_checked(self, visible_state: bool, position: float) -> None:
        if visible_state:
            if self.infinite_line is None:
                self.infinite_line = self.main_plot_item.addLine(
                    x=None, y=position, pen=pg.mkPen(self.config['style'][self.config['theme']]['norma_line_color'],
                                                     width=3), label='                                            '
                                                                     '                                            '
                                                                     '                       norma')
            self.infinite_line.setPos(position)
        else:
            self.main_plot_item.removeItem(self.infinite_line)
            self.infinite_line = None

    def set_sliding_window_size(self, size: int) -> None:
        self.sliding_window_size = size


if __name__ == '__main__':
    app = QApplication([])
    window = CustomPlot({})
    window.add_trace('I(be)', 'left')
    window.add_trace('I(bdd)', 'left')
    window.add_trace('P(be)', 'right')
    window.add_trace('P(bdd)', 'right')
    window.show()
    app.exec_()
