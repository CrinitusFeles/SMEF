
from pathlib import Path

from pandas import DataFrame
from loguru import logger
from qtpy.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from qtmodern.styles import dark, light
from qtmodern.windows import ModernWindow
from smef.client.custom_plot.CustomPlot import CustomPlot
from smef.fi7000_interface.config import FL7000_Config
from smef.client.pandasModel import DataFrameModel

class Viewer(QtWidgets.QWidget):
    units_changed: QtCore.pyqtSignal = QtCore.pyqtSignal()
    marker_checkbox: QtWidgets.QCheckBox
    norma_checkbox: QtWidgets.QCheckBox
    plot_layout: QtWidgets.QVBoxLayout
    norma_unit_label: QtWidgets.QLabel

    tittle_line_edit: QtWidgets.QLineEdit
    units_rbutton1: QtWidgets.QRadioButton
    units_rbutton2: QtWidgets.QRadioButton
    units_rbutton3: QtWidgets.QRadioButton
    norma_val_spinbox: QtWidgets.QSpinBox
    copy_image_button: QtWidgets.QPushButton
    copy_data_button: QtWidgets.QPushButton
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


    def update_minmax_table(self):
        minmax = self.plotter.minmax
        table = DataFrame({'Мин.': minmax[0], 'Сред.': minmax[1], 'Макс.': minmax[2]})
        model = DataFrameModel(table)

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
            self.units_changed.emit()
            print(units)

    def check_norma(self, state: int):
        self.plotter.plotter_style.norma_line.setVisible(bool(state))

    def copy_data(self) -> None:
        if self.plotter.dataframe.size:
            (t_start, t_stop), (idx_start, idx_stop) = self.plotter.get_visible_time_interval()
            frame_slice = self.plotter.dataframe[idx_start:idx_stop]
            frame_slice.to_clipboard(index=False, decimal=',')
        else:
            logger.error('plotter has no data')

    def copy_image(self) -> None:
        data = self.plotter.copy_image(Path(self.config.settings.images_folder))
        QtWidgets.QApplication.clipboard().setMimeData(data)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_window = Viewer(FL7000_Config())
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec_()