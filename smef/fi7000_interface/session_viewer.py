from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit
from qtmodern.styles import dark, light
from qtmodern.windows import ModernWindow
from smef.fi7000_interface.backend import MainWindow


class SessionViewer(MainWindow):
    def __init__(self, config: dict | None = None, dataframe: pd.DataFrame | None = None):
        super().__init__(config=config, dataframe=dataframe)
        self.setWindowTitle("Session Viewer")
        self.groupBox.hide()
        self.groupBox_3.hide()
        self.groupBox_5.hide()
        self.groupBox_7.hide()
        self.groupBox_8.hide()
        self.groupBox_9.hide()
        self.new_session_button.hide()
        self.open_session_viewer_button.hide()
        self.open_generator_button.hide()
        self.connection_settings_button.hide()
        gr = QGroupBox('Параметры нормы и маркеров')
        norma_layout = QHBoxLayout()
        norma_layout.addWidget(self.norma_checkbox)
        norma_layout.addWidget(self.norma_val_spinbox)
        norma_layout.addWidget(self.norma_unit_label)
        v_layout = QVBoxLayout(gr)
        v_layout.addLayout(norma_layout)
        v_layout.addWidget(self.marker_checkbox)

        self.side_layout.insertWidget(9, gr)

        gr_description = QGroupBox('Описание сессии')
        self.description_layout = QVBoxLayout(gr_description)
        self.description_widget = QTextEdit()
        self.description_layout.addWidget(self.description_widget)
        self.side_layout.insertWidget(7, gr_description)

        self.dataframe = dataframe
        if dataframe:
            # TODO: add traces
            labels = np.split(np.array([label.split(',')[0] for label in list(dataframe) if 'Датчик' in label]), 3)[0]
            [self.plotter.add_trace(label, 'left') for label in labels]
            self.update_plotter()
            [line.setData(self.plotter.data[0], self.plotter.data[i + 1]) for i, line in enumerate(self.plotter.data_line)]
            self.plotter.main_plot_item.setLimits(yMin=-10000, yMax=10000, xMin=self.plotter.data[0][0] - 1000000,
                                                  xMax=self.plotter.data[0][-1] + 1000000)
            self.plotter.main_plot_item.enableAutoRange(axis='y')
            self.plotter.main_plot_item.enableAutoRange(axis='x')
            self.update_minmax_table()

    def change_units(self):
        super(SessionViewer, self).change_units()
        [line.setData(self.plotter.data[0], self.plotter.data[i + 1]) for i, line in enumerate(self.plotter.data_line)]
        self.update_minmax_table()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    df: pd.DataFrame = pd.read_csv('./Output/2022-04-22_21.54.csv', sep=';', decimal=',')
    # print(np.split(np.array([label.split(',')[0] for label in list(df) if 'Датчик' in label]), 3)[0])
    # print(df)
    app = QApplication([])
    light(app)
    w = SessionViewer(dataframe=df)
    mw = ModernWindow(w)
    mw.show()
    app.exec_()
