from __future__ import annotations

import argparse
import datetime
import os
import time
from threading import Thread
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QGroupBox, QHBoxLayout, QVBoxLayout, QTextEdit
from numpy import ndarray
from qtmodern.styles import dark, light
from qtmodern.windows import ModernWindow
from qtpy.uic import loadUi
from smef.connection_settings.ConnectionsSettings import ConnectionsSettings
from smef.PlotterWidget.CustomPlot import CustomPlot

from smef.custom_threading import ThreadWithReturnValue
from smef.demo_server import DemoServer
from smef.fi7000_interface.config import load_config, default_config, create_config, open_file_system
from smef.fi7000_interface.fl7000_driver import FL7000
from smef.fi7000_interface.pandasModel import DataFrameModel
from smef.new_session.NewSession import NewSession
from loguru import logger
from PyQt5.QtWidgets import QApplication
from smef.utils import converter, reverse_convert



class MainWindow(QMainWindow):
    def __init__(self, config=None, dataframe=None):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'mainwindow.ui'), self)
        self.setWindowTitle('СМЭП Клиент v2.0.0')
        if config is None:
            self.config = load_config('config', default_config)
        else:
            self.config = config
        [os.makedirs(folder, exist_ok=True) for folder in [self.config['image_folder'], self.config['session_folder']]]

        # ----- Init interface -----
        #self.minmax_table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.open_generator_button.hide()
        self.plotter_stop_button.setEnabled(False)
        self.plotter_start_button.setEnabled(False)
        self.plotter_interval_spin_box.setValue(self.config['anim_period'] / 1000)
        if self.config['theme'] == 'dark':
            self.dark_theme_checkbox.setChecked(True)
            dark(QApplication.instance())
        # self.calib_freq_spin_box.setMaximum(40000000000)
        # ----- Widgets -----
        self.connections_settings_widget: ConnectionsSettings
        self.session_widget: NewSession
        self.viewer = None
        self.plotter = CustomPlot(self.config)
        # ====================
        self.plot_layout.addWidget(self.plotter)
        self.ip = '10.6.1.95' #№self.config['device_ip']
        self.port_list = self.config['ports']
        self.devices = [FL7000(self.ip, port) for port in self.port_list]
        self.alive_sensors = [False] * len(self.devices)  # sensors with TCP connection
        self.active_sensors = self.config['connected_sensors']  # checkbox status
        self.units = self.config['units']
        self._prev_units_state = self.units
        self.session_data_file = None

        # ----- Connections ------
        self.new_session_button.clicked.connect(self.create_new_session_widget)
        self.connection_settings_button.pressed.connect(self.open_connections_settings_widget)
        self.plotter_start_button.clicked.connect(self.start_plot_button_clicked)
        self.plotter_stop_button.clicked.connect(self.stop_plot_button_clicked)
        self.tittle_line_edit.textChanged.connect(lambda text: self.plotter.set_title(text))
        self.copy_image_button.clicked.connect(lambda: self.plotter.copy_image(self.config['image_folder']))
        self.copy_data_button.clicked.connect(self.copy_data_slot)
        self.plotter_interval_spin_box.valueChanged.connect(self.change_plotter_interval)
        self.slide_window_time_spinbox.valueChanged.connect(self.change_sliding_window_size)
        self.units_rbutton1.clicked.connect(self.change_units)
        self.units_rbutton2.clicked.connect(self.change_units)
        self.units_rbutton3.clicked.connect(self.change_units)
        self.marker_checkbox.stateChanged.connect(self.plotter.set_markers_visible_state)
        self.norma_checkbox.stateChanged.connect(lambda: self.plotter.norma_checked(self.norma_checkbox.checkState(),
                                                                                    self.norma_val_spinbox.value()))
        self.norma_val_spinbox.valueChanged.connect(lambda: self.plotter.norma_checked(self.norma_checkbox.checkState(),
                                                                                       self.norma_val_spinbox.value()))
        self.open_session_viewer_button.clicked.connect(self.open_session_viewer)
        self.dark_theme_checkbox.stateChanged.connect(self.change_theme)
        # =========================

        self.plotter_update_timer = QTimer()
        self.plotter_update_timer.timeout.connect(self.plot_data_process)

        if dataframe is None:
            self.check_alive_probes()
        self.change_sliding_window_size()

        self.dataframe = pd.DataFrame()
        self.dataframe_header = ''

    def check_new_connection_parameters(self):
        self.ip = self.connections_settings_widget.server_ip_line_edit.text()
        self.port_list = self.connections_settings_widget.get_port_values()
        self.devices = [FL7000(self.ip, port) for port in self.port_list]
        self.connections_settings_widget.set_connection_status_labels(self.check_alive_probes())

    def create_new_session_widget(self):
        self.session_widget = NewSession(self.config)
        mw = ModernWindow(self.session_widget)
        self.session_widget.session_inited.connect(self.create_new_session)
        self.session_widget.updtade_sensors_button.clicked.connect(
            lambda: self.session_widget.set_checkbox_enabled(self.check_alive_probes()))
        mw.show()

    def create_new_session(self, file_path):
        self.plotter.clear_plot()
        self.plotter_start_button.setEnabled(True)
        self.dataframe = pd.DataFrame()
        for i, sensor in enumerate(self.config['connected_sensors']):
            self.devices[i].label = ''
            if sensor:
                self.devices[i].label = f'Датчик{i + 1}'
                self.plotter.add_trace(f'Датчик {i + 1}', 'left')
        sensor_labels = [device.label for device in self.devices if device.label != '']
        self.dataframe_header = ['Timestamp', 'Время', 'Дата',
                                 *[f'{sensor_label}, {units}' for units in ['В/м', 'дБмкВ/м', 'Вт/м²']
                                   for sensor_label in sensor_labels], 'Калибровочная частота, кГц']
        self.session_data_file = file_path
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(';'.join(self.dataframe_header) + '\n')
        with open(file_path[:-3] + 'txt', 'a', encoding='utf-8') as file:
            file.write(f'{self.session_widget.session_comment_editor.toPlainText()}\n')
        self.plotter.main_plot_item.enableAutoRange(axis='y')
        self.plotter.main_plot_item.enableAutoRange(axis='x')
        self.plotter.norma_checked(self.norma_checkbox.checkState(), self.norma_val_spinbox.value())

    def update_connection_data(self, config: dict):
        self.config = config
        create_config(self.config['name'], self.config)
        self.ip = self.config['device_ip']
        self.port_list = self.config['ports']
        self.devices = [FL7000(self.ip, port) for port in self.port_list]
        self.connect()
        self.alive_sensors = self.config['alive_sensors']

    def check_alive_probes(self) -> list[bool]:
        self.connect()
        alive_probes: list[bool] = [device.connection_status for device in self.devices]
        self.config['alive_sensors'] = alive_probes
        create_config(self.config['name'], self.config)
        return alive_probes

    def connect(self):
        threads = []
        [threads.append(Thread(name=f'Port {device.port}', target=self.connect_device, args=[device])) for device in self.devices]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    def connect_device(self, device):
        try:
            device.connect_device()
        except ValueError as err:
            logger.error(err)

    def measure_routine(self) -> ndarray:

        threads: list[ThreadWithReturnValue] = []
        for i, device in enumerate(self.devices):
            if self.config['connected_sensors'][i]:
                if self.calib_probs_check_box.isChecked():
                    threads.append(ThreadWithReturnValue(target=device.calibrate_measure,
                                                         args=[self.calib_freq_spin_box.value() * 1000],
                                                         name='sensor ' + str(i) + ' thread'))
                else:
                    threads.append(ThreadWithReturnValue(target=device.read_probe_measure,
                                                         name='sensor ' + str(i) + ' thread'))
        [thread.start() for thread in threads]
        return np.array([thread.join()[3] for thread in threads])

    def calculate_new_dataframe_row(self, data: ndarray) -> pd.DataFrame:
        v_m, dBmkV_m, w_m2 = (data, converter(data, mode=1), converter(data, mode=2))
        return pd.DataFrame({'Timestamp': time.time(),
                             'Время': datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S"),
                             'Дата': datetime.datetime.fromtimestamp(time.time()).strftime("%d.%m.%Y"),
                             **{f'{label}': value for label, value in
                                zip(self.dataframe_header[3:], [*v_m, *dBmkV_m, *w_m2])},
                             'Калибровочная частота, кГц': float(self.calib_freq_spin_box.value())
                             if self.calib_probs_check_box.isChecked() else np.NAN}, index=[0])

    def plot_data_process(self):
        start_time = time.time()
        measurements = self.measure_routine()
        print(f'Measurement time: {time.time() - start_time:.3f}', end='\t')
        if len(measurements) > 0:
            if None not in measurements:
                df: pd.DataFrame = self.calculate_new_dataframe_row(measurements)
                df.to_csv(self.session_data_file, mode='a', header=False, index=False, sep=';', decimal=',')
                self.dataframe = self.dataframe.append(df, ignore_index=True)
                df_units = df.filter(regex=f' {self.units}')
                plot_data = df_units.to_numpy()[0]
                self.plotter.add_points(plot_data)

                # thread = Thread(target=self.plotter.add_points, args=[plot_data], daemon=True, name='plotter thread')
                # thread.start()
                # thread.join()
                self.update_minmax_table()
        print(f'Plotting time: {time.time() - start_time:.3f}')

    def start_plot_button_clicked(self):
        self.plotter_stop_button.setEnabled(True)
        if self.plotter_start_button.text() == 'Старт':
            self.plotter_start_button.setText('Пауза')
            self.plotter_update_timer.start(self.config['anim_period'])
        elif self.plotter_start_button.text() == 'Пауза':
            self.plotter_start_button.setText('Старт')
            self.plotter_update_timer.stop()

    def stop_plot_button_clicked(self):
        self.plotter_stop_button.setEnabled(False)
        self.plotter_start_button.setEnabled(False)
        self.plotter_start_button.setText('Старт')
        self.plotter_update_timer.stop()
        QMessageBox.information(self, 'Сеанс завершен', "Данные по этому сеансу находятся в папке\n" +
                                self.config['last_output_path'], QMessageBox.Ok, QMessageBox.Ok)

    def copy_data_slot(self):
        (t_start, t_stop), (idx_start, idx_stop) = self.plotter.get_visible_time_interval()
        # frame_slice = self.dataframe[self.dataframe['Timestamp'].between(t_start - 0.01, t_stop + 0.01)]
        frame_slice = self.dataframe[idx_start:idx_stop]
        frame_slice.to_clipboard(index=False)

    def change_plotter_interval(self, value: float):
        self.plotter_update_timer.setInterval(int(value * 1000))
        self.change_sliding_window_size()

    def change_sliding_window_size(self):
        val = int(self.slide_window_time_spinbox.value() * 3600 / self.plotter_interval_spin_box.value())
        self.plotter.set_sliding_window_size(val)

    def change_units(self):
        if self.sender().__getattribute__('text') != self.units:
        # if self.sender().text() != self.units:
            self._prev_units_state = self.units
            self.units = self.sender().__getattribute__('text')
            self.update_norma_value()
            self.update_plotter()

    def update_norma_value(self):
        if self.units == 'В/м':
            if self._prev_units_state == 'дБмкВ/м':
                self.norma_val_spinbox.setValue(reverse_convert(self.norma_val_spinbox.value(), mode=2))
            elif self._prev_units_state == 'Вт/м²':
                self.norma_val_spinbox.setValue(reverse_convert(self.norma_val_spinbox.value(), mode=1))
        elif self.units == 'дБмкВ/м':
            if self._prev_units_state == 'В/м':
                if 0.001 >= self.norma_val_spinbox.value() >= 0:
                    self.norma_val_spinbox.setValue(0.001)
                self.norma_val_spinbox.setValue(20 * np.log10(self.norma_val_spinbox.value() * 10**6))
            elif self._prev_units_state == 'Вт/м²':
                self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() * 377)
                if 0.001 >= self.norma_val_spinbox.value() >= 0:
                    self.norma_val_spinbox.setValue(0.001)
                self.norma_val_spinbox.setValue(20 * np.log10(self.norma_val_spinbox.value() * 10**6))
        elif self.units == 'Вт/м²':
            if self._prev_units_state == 'дБмкВ/м':
                self.norma_val_spinbox.setValue(reverse_convert(self.norma_val_spinbox.value(), mode=2))
            self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() / 377)
        else:
            raise ValueError(f'Incorrect unit value: {self.units}')

    def update_plotter(self):
            df_units = self.dataframe.filter(regex=f' {self.units}')
            if df_units.shape[0] > 0:
                plot_data = pd.concat([self.dataframe['Timestamp'], df_units], axis=1)
                plot_data = plot_data.to_numpy().T
                self.plotter.data = plot_data
                # self.minmax_table_view.resizeColumnsToContents()
            self.norma_unit_label.setText(self.units)
            self.plotter.left_axis.setLabel(f"<span style=\"font-size:20px;color:"
                                            f"{self.plotter.config['style'][self.plotter.config['theme']]['axis_labels_color']};"
                                            f"\">{self.config['left_axis']['label']}, {self.units}</span>", units=None)

    def update_minmax_table(self):
        df_units = self.dataframe.filter(regex=f' {self.units}')
        table = pd.DataFrame({'Минимальное': df_units.min(), 'Среднее': df_units.mean(), 'Максимальное': df_units.max()})
        model = DataFrameModel(table)

        self.minmax_table_view.setModel(model)
        self.minmax_table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.minmax_table_view.resizeColumnsToContents()

    def open_connections_settings_widget(self):
        self.connections_settings_widget = ConnectionsSettings(self.config)
        self.connections_settings_widget.server_ping_button.clicked.connect(self.check_new_connection_parameters)
        self.connections_settings_widget.update_data_signal.connect(self.update_connection_data)
        mw = ModernWindow(self.connections_settings_widget)
        mw.show()

    def open_session_viewer(self):
        try:
            file_path = open_file_system()
            if file_path is not None:
                data_frame = pd.read_csv(file_path, sep=';', decimal=',')
                comment = ''
                with open(file_path[:-3] + 'txt', 'r', encoding="utf-8") as f:
                    comment = f.read()
                self.viewer = SessionViewer(config=self.config, dataframe=data_frame)
                self.viewer.description_widget.setText(comment)
                self.viewer.setWindowIcon(QtGui.QIcon('../icon/.ico'))
                self.mw = ModernWindow(self.viewer)
                self.mw.show()
        except Exception as err:
            logger.error(f'Ошибка при открытии файла: {err}')

    def change_theme(self, state: bool):
        if state:
            self.config['theme'] = 'dark'
            dark(QApplication.instance())
        else:
            self.config['theme'] = 'light'
            light(QApplication.instance())
        self.plotter.set_theme(self.config)
        if self.viewer is not None:
            self.viewer.plotter.set_theme(self.config)
        create_config('config', self.config)


class SessionViewer(MainWindow):
    def __init__(self, config: dict | None = None, dataframe: pd.DataFrame | None = None):
        super().__init__(config=config, dataframe=dataframe)

        self.setWindowTitle("Просмотр сеанса")
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
        self.minmax_table_view.setMinimumHeight(180)
        self.side_layout.insertWidget(9, gr)

        gr_description = QGroupBox('Описание сессии')
        self.description_layout = QVBoxLayout(gr_description)
        self.description_widget = QTextEdit()
        self.description_layout.addWidget(self.description_widget)
        self.side_layout.insertWidget(7, gr_description)

        self.dataframe = dataframe
        if dataframe is not None:
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


def main(*args):
    parser = argparse.ArgumentParser(description='СМЭП Клиент')
    parser.add_argument('-d', '--demo', help='start program with demo server',  action='store_true')
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    if args.demo:
        print('Starting demo server')
        server = DemoServer(debug_print=False)
        server.start_server()
    else:
        print('Starting without demo server')
    app = QApplication([])
    main_window = MainWindow()
    mw = ModernWindow(main_window)
    mw.show()
    app.exec_()


if __name__ == '__main__':
    main()
