from dataclasses import dataclass
import time
from typing import Literal
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPen
from pyqtgraph import PlotItem, PlotWidget, AxisItem, TextItem, LabelItem, InfiniteLine, mkPen
from pyqtgraph.graphicsItems.LegendItem import LegendItem
from smef.fi7000_interface.config import FL7000_Config


@dataclass
class PlotterPalette:
    background: str
    axis: Qt.GlobalColor
    legend_background: str
    legend_text_color: str
    label_color: str
    color: str

@dataclass
class PlotterLabels:
    xAxis: str
    yAxis: str
    units: str
    legend: str
    marker: str

class PlotterStyle:
    def __init__(self, widget: PlotWidget, config: FL7000_Config) -> None:
        self.config: FL7000_Config = config
        self.dark_palette = PlotterPalette('#121212',Qt.GlobalColor.white,'#00000020','w','#FFFFFF','white')
        self.light_palette = PlotterPalette('#FFFFFF',Qt.GlobalColor.black,'#08080805','k','#000000','black')
        self.palette: PlotterPalette = self.dark_palette
        self.pw: PlotWidget = widget
        self.plot_item: PlotItem = widget.plotItem
        self.norma_line = InfiniteLine(angle=0, pos=0, movable=False, pen=mkPen(self.config.settings.norma_color,
                                                                               width=3),
                            label='                                                     '
                            '                                                 norma')
        self.norma_line.setVisible(False)
        self.title: str = self.config.settings.plotter_title
        if not self.plot_item:
            raise RuntimeError('Incorrect PlotItem')
        self.plot_item.addItem(self.norma_line)
        self.current_locale: Literal['ru', 'en'] = 'ru'
        self.russian_labels = PlotterLabels('Время', 'Напряженность', 'В/м', 'Датчик ', 'Д')
        self.english_labels = PlotterLabels('Time', 'Electric field', 'V/m', 'Sensor ', 'S')
        self.labels: PlotterLabels = self.russian_labels

        self.left_axis: AxisItem = self.plot_item.getAxis('left')
        self.left_axis.setLabel(f"<span style=\"color:{self.palette.axis};font-size:20px\">{self.labels.xAxis}</span>",
                                units=self.labels.units)
        self.left_axis.enableAutoSIPrefix(enable=False)
        self.bottom_axis: AxisItem = self.plot_item.getAxis('bottom')

        self.left_axis.setTextPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                       Qt.PenJoinStyle.RoundJoin))
        self.left_axis.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                   Qt.PenJoinStyle.RoundJoin))
        font = QtGui.QFont()
        font.setPixelSize(16)
        # left_axis.setStyle(stopAxisAtTick=(True, True))
        self.left_axis.setTickFont(font)

        self.marker_label = TextItem()
        self.marker_label.setPos(time.time() + 60, 1)
        self.marker_label.setFont(QtGui.QFont('Times', 10, QtGui.QFont.Bold))
        self.marker_label.setColor(self.palette.label_color)

        self.legend: LegendItem = self.plot_item.addLegend(brush='#08080805', pen='k', colCount=1, labelTextColor='k',
                                                           labelTextSize='7pt')
        self.set_theme(True)

    def recreate_norma_line(self):
        self.plot_item.addItem(self.norma_line)

    def set_theme(self, is_dark_theme: bool) -> None:
        self.palette = self.dark_palette if is_dark_theme else self.light_palette
        labels: PlotterLabels = self.russian_labels if self.current_locale == 'ru' else self.english_labels
        labelStyle: dict[str, str] = {'color': self.palette.label_color, 'font-size': '12pt'}
        self.left_axis.setTextPen(QPen(self.palette.axis, 1, Qt.PenStyle.SolidLine,
                                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.left_axis.setPen(QPen(self.palette.axis, 1, Qt.PenStyle.SolidLine,
                                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.left_axis.setLabel(labels.yAxis, units=self.left_axis.labelUnits, **labelStyle)
        self.bottom_axis.setPen(QPen(self.palette.axis, 1, Qt.PenStyle.SolidLine,
                                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.bottom_axis.setTextPen(QPen(self.palette.axis, 1, Qt.PenStyle.SolidLine,
                                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.bottom_axis.setLabel(labels.xAxis, units=self.bottom_axis.labelUnits, **labelStyle)
        self.pw.setBackground(self.palette.background)
        self.pw.showGrid(x=True, y=True)
        self.legend.setPen(QPen(self.palette.axis, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                    Qt.PenJoinStyle.RoundJoin))
        self.legend.setBrush(self.palette.legend_background)
        self.legend.setLabelTextColor(self.palette.legend_text_color)
        self.marker_label.setColor(self.palette.label_color)
        self.set_title(self.title)

        for legend_tuple in self.legend.items:
            # legend_item: ItemSample = legend_tuple[0]
            # if isinstance(legend_item.item.opts['pen'], dict):
            #     legend_item.item.opts['pen']['width'] = 5
            label_item: LabelItem = legend_tuple[1]
            label_item.setAttr('color', self.palette.legend_text_color)
            label_item.setText(label_item.text)

    def set_title(self, title: str) -> None:
        self.title = title
        self.plot_item.setTitle(f"<span style=\"color:{self.palette.label_color};font-size:30px;\">{title}</span>")


    def change_locale(self, locale: Literal['en', 'ru'] = 'ru') -> None:
        self.current_locale = locale
        self.labels = self.russian_labels if self.current_locale == 'ru' else self.english_labels
        self.left_axis.setLabel(self.labels.yAxis, units=self.labels.units)
        self.bottom_axis.setLabel(self.labels.xAxis)
        self.legend.clear()
        # for i in range(5):
        #     if self.data_line[i] is not None:
        #         self.legend.addItem(self.data_line[i], self.labels.legend + str(i + 1))