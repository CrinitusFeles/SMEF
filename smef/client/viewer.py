
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from loguru import logger
import pandas as pd
from pandas import DataFrame
from qtpy.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from qtmodern.styles import dark, light
from qtmodern.windows import ModernWindow
from smef.client.custom_plot.CustomPlot import CustomPlot
from smef.fi7000_interface.calibrations import Calibrator, ProbeCalibrator
from smef.fi7000_interface.config import FL7000_Config
from smef.client.pandasModel import DataFrameModel
from smef.utils import get_label

@dataclass
class ProbeData:
    probe_id: str
    calibrator: ProbeCalibrator
    data: pd.DataFrame

class Viewer(QtWidgets.QWidget):
    units_changed: QtCore.pyqtSignal = QtCore.pyqtSignal(int)
    marker_checkbox: QtWidgets.QCheckBox
    norma_checkbox: QtWidgets.QCheckBox
    calib_probs_check_box: QtWidgets.QCheckBox
    plot_layout: QtWidgets.QVBoxLayout
    norma_unit_label: QtWidgets.QLabel

    tittle_line_edit: QtWidgets.QLineEdit
    units_rbutton1: QtWidgets.QRadioButton
    units_rbutton2: QtWidgets.QRadioButton
    units_rbutton3: QtWidgets.QRadioButton
    norma_val_spinbox: QtWidgets.QSpinBox
    copy_image_button: QtWidgets.QPushButton
    copy_data_button: QtWidgets.QPushButton
    calib_freq_spin_box: QtWidgets.QSpinBox
    session_description_text_browser: QtWidgets.QTextBrowser
    minmax_table_view: QtWidgets.QTableView
    def __init__(self, config: FL7000_Config, ui_path: str = '') -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('ui', ui_path or 'viewer.ui'), self)
        self.config: FL7000_Config = config
        self.plotter = CustomPlot(self.config)
        self.plot_layout.addWidget(self.plotter)


        self.marker_checkbox.stateChanged.connect(self.plotter.set_visible_crosshair)
        self.tittle_line_edit.textChanged.connect(self.plotter.plotter_style.set_title)
        self.units_rbutton1.toggled.connect(self.change_units)
        self.units_rbutton2.toggled.connect(self.change_units)
        self.units_rbutton3.toggled.connect(self.change_units)
        self.norma_checkbox.stateChanged.connect(self.check_norma)
        self.copy_data_button.pressed.connect(self.copy_data)
        self.copy_image_button.pressed.connect(self.copy_image)

        self.norma_val_spinbox.valueChanged.connect(self.plotter.plotter_style.norma_line.setPos)

        self.change_theme(self.config.settings.dark_theme)
        self.current_units: int = 0

        self.dataframes: list[DataFrame] = []
        self.calib_dataframes:list[DataFrame] = []
        self.sensors_data: list[ProbeData] = []

    def update_minmax_table(self):
        minmax: DataFrame = self.plotter.minmax
        model = DataFrameModel(minmax)
        self.minmax_table_view.setModel(model)
        # self.minmax_table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.minmax_table_view.resizeColumnsToContents()

    def change_theme(self, state: bool) -> None:
        self.plotter.plotter_style.set_theme(state)
        self.config.settings.dark_theme = state
        self.config.write_config()
        dark(QtWidgets.QApplication.instance()) if state else light(QtWidgets.QApplication.instance())

    def change_units(self, state: bool) -> None:
        sender: QtWidgets.QRadioButton = self.sender()  # type: ignore
        if state:
            units: str = sender.text()
            if units == 'В/м':
                self.current_units = 0
            elif units == 'дБмкВ/м':
                self.current_units = 1
            elif units == 'Вт/м²':
                self.current_units = 2
            self.norma_unit_label.setText(units)
            self.plotter.plotter_style.left_axis.setLabel(self.plotter.plotter_style.labels.yAxis, units)
            self.units_changed.emit(self.current_units)
            self.plotter.auto_scale()

    def check_norma(self, state: int):
        self.plotter.plotter_style.norma_line.setVisible(bool(state))

    def copy_image(self) -> None:
        data = self.plotter.copy_image(Path(self.config.settings.images_folder))
        QtWidgets.QApplication.clipboard().setMimeData(data)

    def load_session(self, path: Path, calibrator: Calibrator):
        self.setWindowTitle(f'Результаты сеанса {path.stem}')
        self.plotter.delete_all_data()
        self.sensors_data = [ProbeData(file.stem, calibrator(file.stem),
                                       pd.read_csv(path.joinpath(file.name), sep='\t', decimal=',', encoding='utf-8'))
                             for file in path.glob("*.csv")]
        [self.plotter.add_data_line(f'{get_label(sensor.probe_id)}({sensor.probe_id})') for sensor in self.sensors_data]
        if not len(self.sensors_data):
            logger.error(f'No session data in folder {path}')
            return
        dataframes = [sensor.data.iloc[:, [0, 4]] for sensor in self.sensors_data]
        ts_start: float = dataframes[0].iat[0, 0]
        ts_stop: float = dataframes[0].iat[-1, 0]
        self.plotter.canvas.setLimits(yMin=-10000, yMax=10000, xMin=ts_start - 5000, xMax=ts_stop + 5000)
        self.update_plotter()
        with open(path.joinpath('description.txt')) as file:
            self.session_description_text_browser.setText(file.read())


    def update_plotter(self) -> None:
        if self.calib_probs_check_box.isChecked():
            self.calib_dataframes = [sensor.calibrator.calibrate_dataframe(self.calib_freq_spin_box.value(),
                                                                sensor.data) for sensor in self.sensors_data]
            df_calib: list[DataFrame] = [df.iloc[:, [0, 4 + self.current_units]] for df in self.calib_dataframes]
            self.plotter.plot_df(df_calib)
        else:
            self.dataframes = [sensor.data  for sensor in self.sensors_data]
            df: list[DataFrame] = [sensor.data.iloc[:, [0, 4 + self.current_units]]
                                             for sensor in self.sensors_data]
            self.plotter.plot_df(df)
        self.update_minmax_table()
        self.plotter.auto_scale()

    def copy_data(self) -> None:
        start, finish = self.plotter.get_visible_range()
        df_list: list[DataFrame] = self.calib_dataframes if self.calib_probs_check_box.isChecked() else self.dataframes
        frame_slice: list[pd.DataFrame] = [data[data['Timestamp'].between(start, finish)] for data in df_list]
        df: pd.DataFrame = reduce(lambda left, right: pd.merge_asof(left, right, on='Timestamp', tolerance=10),
                            frame_slice)
        df.iloc[1:].to_clipboard(index=False, decimal=',')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_window = Viewer(FL7000_Config())
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec_()
