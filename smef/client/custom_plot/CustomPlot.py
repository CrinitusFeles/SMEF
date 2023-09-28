
from datetime import datetime
from pathlib import Path
import sys
import pandas as pd
from PyQt5.QtCore import QPointF, QMimeData, QUrl
from pyqtgraph.exporters import ImageExporter
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotWidget
from pyqtgraph.graphicsItems.LegendItem import PlotDataItem
import numpy as np
import numpy.typing as npt
from smef.client.custom_plot.plotter_style import PlotterStyle
from smef.fi7000_interface.config import FL7000_Config
from smef.utils import TimeAxisItem, timestamp


class CustomPlot(QWidget):
    plotter_layout: QVBoxLayout
    def __init__(self, config: FL7000_Config) -> None:
        QWidget.__init__(self)
        self.plotter_layout = QVBoxLayout()
        self.setLayout(self.plotter_layout)

        self.pw = PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotter_style = PlotterStyle(self.pw, config)
        self.main_plot_item: PlotItem = self.plotter_style.plot_item

        self.plotter_layout.addWidget(self.pw)
        self.sliding_window_size = 3600

        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.timestamps: npt.NDArray = np.array([], float)
        self.data: npt.NDArray = np.array([], float)
        self.minmax: npt.NDArray = np.array([], float)
        self.dataframe = pd.DataFrame()


        self.main_plot_item.setLimits(yMin=-10000, yMax=10000, xMin=timestamp(), xMax=timestamp() + 50000000)

        # cross hair
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=2))
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g', width=2))
        self.main_plot_item.addItem(self.plotter_style.marker_label, ignoreBounds=True)
        self.main_plot_item.addItem(self.cursor_vLine, ignoreBounds=True)
        self.main_plot_item.addItem(self.cursor_hLine, ignoreBounds=True)


        self.visible_crosshair: bool = True
        self.freeze_cursor: bool = False

        self.last_mouse_position: QPointF = QPointF(0, 0)
        self.data_lines: list[PlotDataItem] = []

        self.proxy = pg.SignalProxy(self.main_plot_item.scene().sigMouseMoved, rateLimit=100, slot=self.mouse_moved)

    def set_visible_crosshair(self, state: bool) -> None:
        self.visible_crosshair = state
        self.plotter_style.marker_label.setVisible(state)
        self.cursor_vLine.setVisible(state)
        self.cursor_hLine.setVisible(state)

    def add_data_line(self, name: str, color: str):
        dataline: PlotDataItem = self.main_plot_item.plot(name=name, pen={'color': color, 'width': 1})
        dataline.setDownsampling(auto=True)
        self.data_lines.append(dataline)
        if self.data.shape[0] == 0:
            self.data = np.array([[]])
        else:
            self.data = np.vstack((self.data, np.array([], float)))

    def auto_scale(self):
        # self.right_axis_view_box.setYRange()
        self.main_plot_item.enableAutoRange(axis='y')
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
        if not self.main_plot_item.vb:
            raise RuntimeError('Incorrent ViewBox type')
        if not self.main_plot_item.vb.sceneBoundingRect().contains(pos):
            return None
        self.last_mouse_position = pos
        mouse_point: QPointF = self.main_plot_item.vb.mapSceneToView(pos)
        marker_text: str = ''
        for i, data in enumerate(self.data):
            # if len(data) > 0:
            index = np.where(self.timestamps.astype(int) == int(mouse_point.x()))[0]
            if len(index) > 0 and self.data_lines[i] is not None:
                label = self.data_lines[i].name().split()[-1]
                marker_text += f'{self.plotter_style.labels.marker}{label}: {data[index[0]]:.2f}\n'
        marker_text = marker_text[:-1]
        self.plotter_style.marker_label.setText(marker_text)
        self.plotter_style.marker_label.setPos(mouse_point)

        self.cursor_vLine.setPos(mouse_point.x())
        self.cursor_hLine.setPos(mouse_point.y())

    def read_file(self, file_path: Path | str) -> None:
        df: pd.DataFrame = pd.read_csv(file_path, sep='\t', delimiter=',', encoding='utf-8')
        self.timestamps = df['Timestamps'].to_numpy()
        self.data = df.to_numpy()

    def mouseDoubleClickEvent(self, ev) -> None:
        super().mouseDoubleClickEvent(ev)
        self.freeze_cursor = not self.freeze_cursor

    def update_plot_data(self, y_data: np.ndarray, x: datetime | None = None) -> None:
        x_value: datetime = x or datetime.now()
        ts: float = x_value.timestamp()
        self.timestamps = np.append(self.timestamps, ts)
        self.data = np.hstack((self.data[:self.data.shape[0]], y_data[:self.data.shape[0]].reshape(self.data.shape[0],
                                                                                                   1)))
        for data_line, y in zip(self.data_lines, self.data):
            data_line.setData(self.timestamps, y)

        self.minmax = np.row_stack((np.amin(self.data, axis=1), np.mean(self.data, axis=1), np.amax(self.data, axis=1)))
        self.mouse_moved((self.last_mouse_position))

    def plot_df(self, data: np.ndarray) -> None:
        self.timestamps = data[0]
        self.data = data[1:]
        for data_line, y in zip(self.data_lines, data[1:]):
            data_line.setData(self.timestamps, y)
        self.minmax = np.row_stack((np.amin(self.data, axis=1), np.mean(self.data, axis=1), np.amax(self.data, axis=1)))

    def set_sliding_window_size(self, window_size_sec: int) -> None:
        self.sliding_window_size = window_size_sec

    def clear_plot(self) -> None:
        self.pw.setXRange(timestamp() - self.sliding_window_size / 2, timestamp() + self.sliding_window_size / 2)
        self.data = np.array([[], [], [], [], []], float)
        for i, data_line in enumerate(self.data_lines):
                data_line.setData(self.data[0], self.data[i + 1])

    def delete_all_data(self) -> None:
        self.data = np.array([], float)
        self.timestamps = np.array([], float)
        self.data_lines = []
        self.main_plot_item.clear()
        self.main_plot_item.addItem(self.plotter_style.marker_label, ignoreBounds=True)
        self.main_plot_item.addItem(self.cursor_vLine, ignoreBounds=True)
        self.main_plot_item.addItem(self.cursor_hLine, ignoreBounds=True)
        self.plotter_style.recreate_norma_line()

    def copy_image(self, folder_path: Path) -> QMimeData:
        Path.mkdir(folder_path, exist_ok=True)
        file_name: str = datetime.now().strftime("%d.%m.%y-%H_%M_%S") + ".png"
        exporter = ImageExporter(self.main_plot_item)
        data = QMimeData()
        data.setUrls([QUrl.fromLocalFile(str(folder_path.joinpath(file_name)))])
        exporter.export(str(folder_path.joinpath(file_name)))
        return data

    def get_visible_time_interval(self):
        x1_timestamp = self.pw.visibleRange().getCoords()[0]
        x2_timestamp = self.pw.visibleRange().getCoords()[2]
        idx_start: int = (np.abs(self.timestamps - x1_timestamp)).argmin()
        idx_stop: int = (np.abs(self.timestamps - x2_timestamp)).argmin()
        return (self.timestamps[idx_start], self.timestamps[idx_stop]), (idx_start, idx_stop)

if __name__ == '__main__':
    app = QApplication([])
    window = CustomPlot(FL7000_Config())
    window.show()
    sys.exit(app.exec_())
