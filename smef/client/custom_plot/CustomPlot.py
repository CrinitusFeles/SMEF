
from datetime import datetime
from functools import reduce
from pathlib import Path
import sys
import pandas as pd
from PyQt5.QtCore import QPointF, QMimeData, QUrl, QRectF
from pyqtgraph.exporters import ImageExporter
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QSizePolicy
import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotWidget
from pyqtgraph.graphicsItems.LegendItem import PlotDataItem
import numpy as np
from smef.client.custom_plot.plotter_style import PlotterStyle
from smef.fi7000_interface.config import FL7000_Config
from smef.utils import TimeAxisItem, timestamp


class CustomPlot(QWidget):
    def __init__(self, config: FL7000_Config) -> None:
        QWidget.__init__(self)
        self.plotter_layout = QVBoxLayout()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(300)
        self.setLayout(self.plotter_layout)

        self.pw = PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotter_style = PlotterStyle(self.pw, config)
        self.canvas: PlotItem = self.plotter_style.plot_item

        self.plotter_layout.addWidget(self.pw)
        self.sliding_window_size = 3600

        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.minmax: pd.DataFrame = pd.DataFrame()

        self.canvas.setLimits(yMin=-10000, yMax=10000, xMin=timestamp(), xMax=timestamp() + 50000000)

        # cross hair
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=2))
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g', width=2))
        self.canvas.addItem(self.plotter_style.marker_label, ignoreBounds=True)
        self.canvas.addItem(self.cursor_vLine, ignoreBounds=True)
        self.canvas.addItem(self.cursor_hLine, ignoreBounds=True)


        self.visible_crosshair: bool = True
        self.freeze_cursor: bool = False

        self.last_mouse_position: QPointF = QPointF(0, 0)
        self.data_lines: list[PlotDataItem] = []
        self.data: list[pd.DataFrame] = []

        self.proxy = pg.SignalProxy(self.canvas.scene().sigMouseMoved, rateLimit=100, slot=self.mouse_moved)

    def set_visible_crosshair(self, state: bool) -> None:
        self.visible_crosshair = state
        self.plotter_style.marker_label.setVisible(state)
        self.cursor_vLine.setVisible(state)
        self.cursor_hLine.setVisible(state)

    def add_data_line(self, name: str, color: str | None = None):
        line_color: str = color or next(self.plotter_style.colors)
        dataline: PlotDataItem = self.canvas.plot(name=name, pen={'color': line_color, 'width': 1})
        dataline.setDownsampling(auto=True)
        self.data_lines.append(dataline)

    def auto_scale(self):
        # self.right_axis_view_box.setYRange()
        self.canvas.enableAutoRange(axis='y')
        self.canvas.enableAutoRange(axis='x')
        # if self.right_axis_view_box is not None:
        #     self.right_axis_view_box.enableAutoRange(axis='y')

    def mouse_moved(self, evt: tuple[QPointF]) -> None:
        if not self.visible_crosshair or self.freeze_cursor:
            return None
        # if self.visible_crosshair and not self.freeze_cursor:
        if isinstance(evt, tuple):
            pos: QPointF = evt[0]  # using signal proxy turns original arguments into a tuple
        else:
            pos = evt
        if not self.canvas.vb:
            raise RuntimeError('Incorrent ViewBox type')
        if not self.canvas.vb.sceneBoundingRect().contains(pos):
            return None
        self.last_mouse_position = pos
        mouse_point: QPointF = self.canvas.vb.mapSceneToView(pos)
        marker_text: str = ''
        for data_line in self.data_lines:
            ticks, data = data_line.getData()
            if ticks is not None and data is not None:
                index = np.where(ticks.astype(int) == int(mouse_point.x()))[0]
                if len(index) > 0:
                    label: str = data_line.name()#.split()[-1]
                    marker_text += f'{self.plotter_style.labels.marker}{label}: {data[index[0]]:.2f}\n'
        marker_text = marker_text[:-1]
        self.plotter_style.marker_label.setText(marker_text)
        self.plotter_style.marker_label.setPos(mouse_point)

        self.cursor_vLine.setPos(mouse_point.x())
        self.cursor_hLine.setPos(mouse_point.y())

    def mouseDoubleClickEvent(self, ev) -> None:
        super().mouseDoubleClickEvent(ev)
        self.freeze_cursor = not self.freeze_cursor

    def plot_df(self, data: list[pd.DataFrame]) -> None:
        self.data = data
        for data_line, df in zip(self.data_lines, data):
            np_data = df.to_numpy().T
            data_line.setData(np_data[0], np_data[1])
        sensor_data = pd.concat([df.iloc[:, [1]] for df in data], axis=1)
        self.minmax = pd.concat([sensor_data.min(), sensor_data.mean(), sensor_data.max()], axis=1)
        self.minmax.columns = ['Мин.', 'Средн.', 'Макс.']

    def set_sliding_window_size(self, window_size_sec: int) -> None:
        self.sliding_window_size = window_size_sec

    # def clear_plot(self) -> None:
    #     self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
    #     self.data = np.array([[], [], [], [], []], float)
    #     for i, data_line in enumerate(self.data_lines):
    #             data_line.setData(self.data[0], self.data[i + 1])

    def delete_all_data(self) -> None:
        self.data_lines = []
        self.canvas.clear()
        self.canvas.addItem(self.plotter_style.marker_label, ignoreBounds=True)
        self.canvas.addItem(self.cursor_vLine, ignoreBounds=True)
        self.canvas.addItem(self.cursor_hLine, ignoreBounds=True)
        self.plotter_style.recreate_norma_line()
        self.plotter_style.restart_generator()

    def copy_image(self, folder_path: Path) -> QMimeData:
        Path.mkdir(folder_path, exist_ok=True)
        file_name: str = datetime.now().strftime("%d.%m.%y-%H_%M_%S") + ".png"
        exporter = ImageExporter(self.canvas)
        data = QMimeData()
        data.setUrls([QUrl.fromLocalFile(str(folder_path.joinpath(file_name)))])
        exporter.export(str(folder_path.joinpath(file_name)))
        return data


    def copy_data(self) -> None:
        start, finish = self.get_visible_range()
        frame_slice: list[pd.DataFrame] = [data[data['Timestamp'].between(start, finish)] for data in self.data]
        df: pd.DataFrame = reduce(lambda left, right: pd.merge_asof(left, right, on='Timestamp', tolerance=10),
                                    frame_slice)
        df.iloc[1:].to_clipboard(index=False, decimal=',')

    def get_visible_range(self) -> tuple[float, float]:
        if not self.canvas.vb:
            raise RuntimeError('None view box!')
        rect: QRectF = self.canvas.vb.viewRect()
        return rect.left() - 1,  rect.left() + rect.width() + 0.5

if __name__ == '__main__':
    app = QApplication([])
    window = CustomPlot(FL7000_Config())
    window.show()
    sys.exit(app.exec_())
