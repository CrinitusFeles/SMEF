import socket
import os
import time
import pandas as pd
import sys
import pyqtgraph as pg
import pyqtgraph.exporters
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Lock
import mainwindow
import numpy as np
import Config
import json
from SessionViewer import SessionViewer
from NewSession import NewSession
from ConnectionsSettings import ConnectionsSettings
import utils
from custom_threading import ThreadWithReturnValue
from GeneratorSettings import GeneratorSettings
from sensor_commands import *

logger = app_logger.get_logger(__name__)


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("СМЭП КЛИЕНТ")
        self.config_file_name = 'config.json'
        self.output_folder = os.getcwd() + '\\output'
        self.event_log_folder = os.getcwd() + '\\event_log'
        self.images_folder = self.output_folder + '\\images'
        if not os.path.isdir(self.output_folder):
            logger.info(f'Create new output folder {self.output_folder}')
            os.mkdir(self.output_folder)
        else:
            logger.info('Output folder exists')
        self.server_ip = '10.6.1.95'
        self.sensors_port = [4001, 4002, 4003, 4004, 4005]
        self.sensors_amount = 0
        self.generator_ip = ''
        self.alive_sensors = [False, False, False, False, False]  # sensors with TCP connection
        self.active_sensors = [False, False, False, False, False]  # checkbox status
        self.threads = [None, None, None, None, None]
        self.lock = Lock()
        self.socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM)]

        self.send_all_sensors_parallel(self.threads, self.connect)

        print(self.alive_sensors)
        self.generator_settings_widget = GeneratorSettings()
        self.connections_settings_widget = None
        self.session_settings_widget = None
        self.viewer = None
        self.config_obj = None
        self.df = None
        self.table = None

        self.app = app

        self.start_button.pressed.connect(self.new_session)
        self.stop_button.pressed.connect(self.stop_session)
        self.stop_button.setEnabled(False)
        self.graph_start_button.pressed.connect(self.start_plot)
        self.graph_start_button.setEnabled(False)
        self.open_generator_button.pressed.connect(self.open_generator_settings)
        self.open_button.pressed.connect(self.open_session)
        self.connection_settings_button.pressed.connect(self.open_connections_settings)
        self.norma_checkbox.stateChanged.connect(self.norma_checked)
        self.slide_window_time_spinbox.valueChanged.connect(self.change_sliding_window_size)
        self.norma_val_spinbox.valueChanged.connect(self.norma_checked)
        self.copy_graph_button.pressed.connect(self.copy_image)
        self.units_rbutton1.toggled.connect(self.update_units)
        self.units_rbutton2.toggled.connect(self.update_units)
        self.units_rbutton3.toggled.connect(self.update_units)
        self.tittle_line_edit.textChanged.connect(self.set_title)
        self.copy_data_button.pressed.connect(self.copy_data)
        self.measure_interval_line_edit.valueChanged.connect(self.set_measure_interval)

        self.data_update_timer = QtCore.QTimer()
        self.update_period = 1000
        self.data_update_timer.setInterval(self.update_period)
        self.data_update_timer.timeout.connect(self.read_probe_data)

        if not self.search_config_file():
            logger.warning("Config file does not exist. Set default settings")
            self.config_obj = Config.Config()
            utils.create_json_file(self.config_obj, self.config_file_name)

            # create widget object and fill its fields by config file
            self.session_settings_widget = NewSession()
            self.session_settings_widget.path_line_edit.setText(self.config_obj.last_path)
            self.session_settings_widget.filename_line_edit.setText(self.config_obj.last_name)
            self.session_settings_widget.s1_checkbox.setChecked(self.config_obj.connected_sensors[0])
            self.session_settings_widget.s2_checkbox.setChecked(self.config_obj.connected_sensors[1])
            self.session_settings_widget.s3_checkbox.setChecked(self.config_obj.connected_sensors[2])
            self.session_settings_widget.s4_checkbox.setChecked(self.config_obj.connected_sensors[3])
            self.session_settings_widget.s5_checkbox.setChecked(self.config_obj.connected_sensors[4])
            self.session_settings_widget.accept_button.pressed.connect(self.init_new_session)
            self.session_settings_widget.updtade_sensors_button.pressed.connect(self.update_sensors)

            self.connections_settings_widget = ConnectionsSettings()
        else:
            logger.info("Config exists. Settings loaded from file")
            try:
                with open(self.config_file_name, "r+", encoding='utf8') as read_file:
                    self.config_obj = Config.Config()
                    self.config_obj.__dict__ = json.load(read_file)
                    self.server_ip = self.config_obj.terminal_server_ip
                    self.sensors_port[0] = self.config_obj.sensor1_port
                    self.sensors_port[1] = self.config_obj.sensor2_port
                    self.sensors_port[2] = self.config_obj.sensor3_port
                    self.sensors_port[3] = self.config_obj.sensor4_port
                    self.sensors_port[4] = self.config_obj.sensor5_port
                    self.generator_ip = self.config_obj.generator_ip
                    self.generator_port = self.config_obj.generator_port
                    self.units = self.config_obj.units
                    self.update_units(self.units)
                    self.norma_val_spinbox.setValue(self.config_obj.norma_val)
                    self.norma_checkbox.setChecked(self.config_obj.norma)

                    self.session_settings_widget = NewSession(path=self.config_obj.last_path,
                                                              name=self.config_obj.last_name,
                                                              s1=self.config_obj.connected_sensors[0],
                                                              s2=self.config_obj.connected_sensors[1],
                                                              s3=self.config_obj.connected_sensors[2],
                                                              s4=self.config_obj.connected_sensors[3],
                                                              s5=self.config_obj.connected_sensors[4])
                    self.session_settings_widget.accept_button.pressed.connect(self.init_new_session)
                    self.session_settings_widget.updtade_sensors_button.pressed.connect(self.update_sensors)

                    self.connections_settings_widget = ConnectionsSettings(server_ip=self.config_obj.terminal_server_ip,
                                                                           s1_port=self.config_obj.sensor1_port,
                                                                           s2_port=self.config_obj.sensor2_port,
                                                                           s3_port=self.config_obj.sensor3_port,
                                                                           s4_port=self.config_obj.sensor4_port,
                                                                           s5_port=self.config_obj.sensor5_port,
                                                                           generator_ip=self.config_obj.generator_ip,
                                                                           generator_port=self.config_obj.generator_port
                                                                           )

            except Exception as error:
                print(error)

        self.set_enable_sensors_checkbox()

        with open('config.json', 'r+', encoding='utf8') as f:
            d = json.load(f)
            logger.info(json.dumps(d, indent=4, sort_keys=True))

    def connect(self, sock, ip, port):
        try:
            print(f'trying to connect to {ip}:{port}')
            sock.connect((ip, port))
            sock.settimeout(2)
            return read_sensor_ident(sock)
        except Exception as ex:
            print(ex)
            return False

    def disconnect(self, sock):
        try:
            sock.close()
            logger.info(f'{sock} disconnected')
            return False
        except Exception as ex:
            logger.error(f'Socket disconnection error')
            return False

    def update_sensors(self):
        self.send_all_sensors_parallel(self.threads, self.disconnect)
        self.socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
        self.send_all_sensors_parallel(self.threads, self.connect)
        self.set_enable_sensors_checkbox()

    def set_enable_sensors_checkbox(self):
        if not self.alive_sensors[0]:
            self.session_settings_widget.s1_checkbox.setChecked(False)
            self.session_settings_widget.s1_checkbox.setEnabled(False)
        else:
            self.session_settings_widget.s1_checkbox.setEnabled(True)
        if not self.alive_sensors[1]:
            self.session_settings_widget.s2_checkbox.setChecked(False)
            self.session_settings_widget.s2_checkbox.setEnabled(False)
        else:
            self.session_settings_widget.s2_checkbox.setEnabled(True)
        if not self.alive_sensors[2]:
            self.session_settings_widget.s3_checkbox.setChecked(False)
            self.session_settings_widget.s3_checkbox.setEnabled(False)
        else:
            self.session_settings_widget.s3_checkbox.setEnabled(True)
        if not self.alive_sensors[3]:
            self.session_settings_widget.s4_checkbox.setChecked(False)
            self.session_settings_widget.s4_checkbox.setEnabled(False)
        else:
            self.session_settings_widget.s4_checkbox.setEnabled(True)
        if not self.alive_sensors[4]:
            self.session_settings_widget.s5_checkbox.setChecked(False)
            self.session_settings_widget.s5_checkbox.setEnabled(False)
        else:
            self.session_settings_widget.s5_checkbox.setEnabled(True)

    def send_all_sensors_parallel(self, threads, function):
        for sock, port, i in zip(self.socket, self.sensors_port, range(5)):
            if function == self.connect:
                threads[i] = ThreadWithReturnValue(target=function, args=(sock, self.server_ip, port),
                                                   name=f'sensor {i} thread')
            else:
                threads[i] = ThreadWithReturnValue(target=function, args=[sock],
                                                   name=f'sensor {i} thread')
            threads[i].start()
        for i in range(5):
            self.alive_sensors[i] = threads[i].join()

    def open_generator_settings(self):
        self.generator_settings_widget.show()

    def open_connections_settings(self):
        self.connections_settings_widget.show()

    def open_session(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.open()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_full_path = str(file_dialog.selectedFiles()[0])
            print(file_full_path)
            log = pd.read_csv(file_full_path, sep=';', decimal=',')
            print(list(log))
            if 'Time' in log:
                self.viewer = SessionViewer(data=log)
                self.viewer.show()
            else:
                logger.error(f'Incorrect log file {file_full_path}')
                QMessageBox.warning(self, 'Внимание!', "Выбран некорректный файл лога.", QMessageBox.Ok, QMessageBox.Ok)
                return

            # data = pd.concat([log['Timestamp'], log['Sensor1'], log['Sensor2'], log['Sensor3'], log['Sensor4'],
            #                   log['Sensor5']], axis=1)
            # table = pd.concat([log['min'], log['aver'], log['max']], axis=1)
            # print(table)

            # self.path_line_edit.setText(file_full_path)

    def send_to_connected_sensors(self, sock, threads):
        fields = [[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]]
        for s in [i for i, x in enumerate(self.alive_sensors) if x]:
            # fields[i] = read_single_probe(sock)
            threads[s] = ThreadWithReturnValue(target=read_single_probe, args=[sock[s]], name=f'sensor {s} thread')
            threads[s].start()
        for s in [i for i, x in enumerate(self.alive_sensors) if x]:
            fields[s] = threads[s].join()
        return fields

    def read_probe_data(self):
        fields = self.send_to_connected_sensors(self.socket, self.threads)

        self.customplot.pgcustom.sensor1 = fields[0][3]
        self.customplot.pgcustom.sensor2 = fields[1][3]
        self.customplot.pgcustom.sensor3 = fields[2][3]
        self.customplot.pgcustom.sensor4 = fields[3][3]
        self.customplot.pgcustom.sensor5 = fields[4][3]
        self.customplot.pgcustom.update_plot_data()

        if self.log_checkbox.isChecked():
            try:
                with open(self.session_settings_widget.path_line_edit.text() + '\\' +
                          self.session_settings_widget.filename_line_edit.text() + '.csv', 'a+') as log:
                    log_string = str(time.time()).replace('.', ',') + ';' + str(time.strftime("%H:%M:%S \\ %d.%m.%Y")) + ';'
                    if self.session_settings_widget.s1_checkbox.isChecked():
                        log_string += str(fields[0][3]).replace('.', ',') + ';'
                    if self.session_settings_widget.s2_checkbox.isChecked():
                        log_string += str(fields[1][3]).replace('.', ',') + ';'
                    if self.session_settings_widget.s3_checkbox.isChecked():
                        log_string += str(fields[2][3]).replace('.', ',') + ';'
                    if self.session_settings_widget.s4_checkbox.isChecked():
                        log_string += str(fields[3][3]).replace('.', ',') + ';'
                    if self.session_settings_widget.s5_checkbox.isChecked():
                        log_string += str(fields[4][3]).replace('.', ',') + ';'
                    log.write(log_string[:-1] + '\n')
            except Exception as ex:
                logger.error(f'Write log file error: {ex}')
                QMessageBox.warning(self, 'Warning!', 'Проблема с доступом к файлу лога', QMessageBox.Ok,
                                        QMessageBox.Ok)
                self.customplot.pgcustom.stop()
                self.data_update_timer.stop()
                self.graph_start_button.setText('Старт')

        minmax = self.customplot.pgcustom.minmax
        self.table = pd.DataFrame({'min': minmax[0], 'aver': minmax[1], 'max': minmax[2]})
        for i, row in self.table.iterrows():
            for j in range(self.minmax_values_table.columnCount()):
                if self.active_sensors[i]:
                    self.minmax_values_table.setItem(i, j, QTableWidgetItem('{:.2f}'.format(row[j])))
                else:
                    break

        self.customplot.pgcustom.update_plot_data()
        app.processEvents()
        return fields

    def new_session(self):
        # print(self.session_settings_widget)
        self.session_settings_widget.show()

    def start_plot(self):
        self.stop_button.setEnabled(True)
        if self.graph_start_button.text() == 'Старт':
            self.data_update_timer.start(self.update_period)
            self.customplot.pgcustom.start()
            self.graph_start_button.setText('Пауза')
        elif self.graph_start_button.text() == 'Пауза':
            self.customplot.pgcustom.stop()
            self.data_update_timer.stop()
            self.graph_start_button.setText('Старт')

    def norma_checked(self):
        # line = InfiniteLine(pos=1.0, pen=pg.mkPen('r', width=13))
        # self.customplot.pgcustom.addItem(line)
        val = self.norma_val_spinbox.value()
        state = self.norma_checkbox.checkState()
        if self.customplot.pgcustom.infinite_line is not None:
            self.customplot.pgcustom.removeItem(self.customplot.pgcustom.infinite_line)
            self.customplot.pgcustom.infinite_line = None
        if state == 2:
            self.customplot.pgcustom.infinite_line = self.customplot.pgcustom.addLine(
                x=None, y=val, pen=pg.mkPen('r', width=3), label='                                                     '
                                                                 '                                                     '
                                                                 '     norma')
        else:
            self.customplot.pgcustom.removeItem(self.customplot.pgcustom.infinite_line)
            self.customplot.pgcustom.infinite_line = None
            pass

    @staticmethod
    def converter(value, mode):
        if mode == 1:  # В/м -> дБмкВ/м
            return 20 * np.log10(value * 10**6)
        elif mode == 2:  # В/м -> Вт/м2
            return value / 377
        else:
            raise Exception
    
    def copy_image(self):
        try:
            if not os.path.isdir(self.images_folder):
                logger.info(f'Create new images folder {self.images_folder}')
                os.mkdir(self.images_folder)
            else:
                logger.info('Images folder exists')
            file_name = datetime.datetime.now().strftime("\\%d.%m.%y-%H_%M_%S") + ".png"
            exporter = pg.exporters.ImageExporter(self.customplot.pgcustom.plotItem)
            url = QtCore.QUrl.fromLocalFile(self.images_folder + file_name)
            print(url)
            data = QtCore.QMimeData()
            data.setUrls([url])
            self.app.clipboard().setMimeData(data)
            exporter.export(self.images_folder + file_name)
            # os.remove('x:/SMEP/' + file_name)
            
        except Exception as ex:
            print(ex)

    def copy_data(self):
        x1_timestamp = self.customplot.pgcustom.visibleRange().getCoords()[0]
        x2_timestamp = self.customplot.pgcustom.visibleRange().getCoords()[2]
        x = self.customplot.pgcustom.data[0]
        mask = np.array((x > x1_timestamp) & (x < x2_timestamp))
        data = self.customplot.pgcustom.data[:, mask]
        self.df = pd.DataFrame({'Timestamp': data[0].astype(int),
                                'Time': [datetime.datetime.fromtimestamp(x).strftime("%H:%M:%S \\ %d.%m.%Y") for x in
                                         data[0].astype(int)],
                                'Sensor1': data[1],
                                'Sensor2': data[2],
                                'Sensor3': data[3],
                                'Sensor4': data[4],
                                'Sensor5': data[5]})

        self.df['Sensor1'] = self.df['Sensor1'].astype(str).str.replace('.', ',', regex=False)
        self.df['Sensor2'] = self.df['Sensor2'].astype(str).str.replace('.', ',', regex=False)
        self.df['Sensor3'] = self.df['Sensor3'].astype(str).str.replace('.', ',', regex=False)
        self.df['Sensor4'] = self.df['Sensor4'].astype(str).str.replace('.', ',', regex=False)
        self.df['Sensor5'] = self.df['Sensor5'].astype(str).str.replace('.', ',', regex=False)

        if not self.session_settings_widget.s1_checkbox.isChecked():
            del self.df['Sensor1']
        if not self.session_settings_widget.s2_checkbox.isChecked():
            del self.df['Sensor2']
        if not self.session_settings_widget.s3_checkbox.isChecked():
            del self.df['Sensor3']
        if not self.session_settings_widget.s4_checkbox.isChecked():
            del self.df['Sensor4']
        if not self.session_settings_widget.s5_checkbox.isChecked():
            del self.df['Sensor5']

        self.df.to_clipboard(index=False)
        # print(app.clipboard().text())

        # log = pd.concat([self.df, pd.DataFrame({'----': ['']*5}),
        #                  pd.DataFrame({'': ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5']}),
        #                  self.table,
        #                  pd.DataFrame({'norma': [self.norma_val_spinbox.value()]}),
        #                  pd.DataFrame({'units': [self.units]})], axis=1)

    def change_sliding_window_size(self):
        val = self.slide_window_time_spinbox.value() * 60 // self.measure_interval_line_edit.value()
        self.customplot.pgcustom.sliding_window_size = val
        if len(self.customplot.pgcustom.data[0]) > 0:
            self.customplot.pgcustom.data = self.customplot.pgcustom.data[:, -self.customplot.pgcustom.sliding_window_size:]

    def set_measure_interval(self):
        self.update_period = self.measure_interval_line_edit.value() * 1000
        self.data_update_timer.setInterval(self.update_period)
        self.slide_window_time_spinbox.setValue(self.customplot.pgcustom.sliding_window_size // 60 * self.measure_interval_line_edit.value())
        self.change_sliding_window_size()

    def update_units(self, units=None):
        if units is None:
            try:
                if self.units_rbutton1.isChecked():
                    self.units = 'В/м'
                    self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(False)
                    self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                elif self.units_rbutton2.isChecked():
                    self.units = 'дБмкВ/м'
                    self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(True)
                    self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                else:
                    self.units = 'Вт/м2'
                    self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(False)
                    self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                self.norma_unit_label.setText(self.units)
            except Exception as ex:
                print(ex)
        else:  # after load config file
            if units == 'В/м':
                self.units_rbutton1.setChecked(True)
                self.units = 'В/м'
            elif units == 'дБмкВ/м':
                self.units_rbutton2.setChecked(True)
                self.units = 'дБмкВ/м'
            elif units == 'Вт/м2':
                self.units_rbutton3.setChecked(True)
                self.units = 'Вт/м2'
            self.update_units()

    def set_title(self):
        new_tittle = self.tittle_line_edit.text()
        item = self.customplot.pgcustom.getPlotItem()
        item.setTitle("<span style=\"color:black;font-size:30px\">" + new_tittle + "</span>")

    def set_y_axis_label(self):
        self.customplot.pgcustom.getPlotItem().setLabel('left', "<span style=\"color:black;font-size:20px\">" +
                                                        self.plot_y_label_line_edit.text() + "</span>", units="°C")

    def set_x_axis_label(self):
        self.customplot.pgcustom.getPlotItem().setLabel('bottom', "<span style=\"color:black;font-size:20px\">" +
                                                        self.plot_x_label_line_edit.text() + "</span>")

    def search_config_file(self):
        return os.path.isfile(self.config_file_name) and os.stat(self.config_file_name).st_size != 0

    def init_new_session(self):
        if self.session_settings_widget.status:
            self.graph_start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.sensors_amount = 0
            self.active_sensors = [False, False, False, False, False]
            if self.session_settings_widget.s1_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[0] = True
            if self.session_settings_widget.s2_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[1] = True
            if self.session_settings_widget.s3_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[2] = True
            if self.session_settings_widget.s4_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[3] = True
            if self.session_settings_widget.s5_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[4] = True
            self.output_folder = self.session_settings_widget.path_line_edit.text()
            self.customplot.pgcustom.clear_plot()
            self.customplot.pgcustom.init_data([self.session_settings_widget.s1_checkbox.isChecked(),
                                                self.session_settings_widget.s2_checkbox.isChecked(),
                                                self.session_settings_widget.s3_checkbox.isChecked(),
                                                self.session_settings_widget.s4_checkbox.isChecked(),
                                                self.session_settings_widget.s5_checkbox.isChecked()])
            logger.info('Start new session with sensors')
            self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)

    def stop_session(self):
        if self.graph_start_button.text() == 'Пауза':
            self.customplot.pgcustom.stop()
            self.data_update_timer.stop()
            self.graph_start_button.setText('Старт')
        QMessageBox.information(self, 'Сеанс завершен', "Данные по этому сеансу находятся в папке\n" +
                                self.session_settings_widget.path_line_edit.text(), QMessageBox.Ok, QMessageBox.Ok)
        self.graph_start_button.setEnabled(False)
        self.stop_button.setEnabled(False)


if __name__ == '__main__':
    logger.info("Start application")
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon2.ico'))

    w = MainWindow()
    w.setWindowIcon(QtGui.QIcon('icon2.ico'))
    w.show()

    app.exec_()
    logger.warning('Stop application')
