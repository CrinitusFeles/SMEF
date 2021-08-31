import argparse
import copy
import socket
from types import SimpleNamespace
import pandas as pd
import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette
from qdarkstyle.light.palette import LightPalette
import pyqtgraph.exporters
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

try:
    from .mainwindow import *
    from .Config import *
    from .SessionViewer import SessionViewer
    from .NewSession import NewSession
    from .ConnectionsSettings import ConnectionsSettings
    from .utils import *
    from .custom_threading import ThreadWithReturnValue
    from .GeneratorSettings import GeneratorSettings
    from .sensor_commands import *
    from .app_logger import *
    from .__init__ import __version__
    from .demo_server import DemoServer
except Exception as ex:
    print(ex)
    from mainwindow import *
    from Config import *
    from SessionViewer import SessionViewer
    from NewSession import NewSession
    from ConnectionsSettings import ConnectionsSettings
    from utils import *
    from custom_threading import ThreadWithReturnValue
    from GeneratorSettings import GeneratorSettings
    from sensor_commands import *
    from app_logger import *
    from __init__ import __version__
    from demo_server import DemoServer


logger = get_logger(__name__)

""" Attention!
LegendItem.py was modified at function 'paint' (361):
            pen = opts['pen']
            color = pen['color']
            p.setPen(fn.mkPen({'color': color, 'width': 5}))
"""


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.config_file_name = 'config.json'
        self.output_folder = os.getcwd() + '/output'
        self.event_log_folder = os.getcwd() + '/event_log'
        self.images_folder = self.output_folder + '/images'
        if not os.path.isdir(self.output_folder):
            logger.info('Create new output folder' + str(self.output_folder))
            os.mkdir(self.output_folder)
        else:
            logger.info('Output folder exists')
        self.server_ip = '127.0.0.1'
        self.sensors_port = [4001, 4002, 4003, 4004, 4005]
        self.sensors_amount = 0
        self.generator_ip = ''
        self.alive_sensors = [False, False, False, False, False]  # sensors with TCP connection
        self.active_sensors = [False, False, False, False, False]  # checkbox status
        self.threads = [None, None, None, None, None]
        self.units_mode = 0
        self.units = 'В/м'

        options = ([('Russian', ''), ('English', os.path.dirname(__file__) + '/ru-eng.qm')])
        self.current_locale = 'ru'
        self.trans = QtCore.QTranslator(self)
        for i, (text, lang) in enumerate(options):
            self.locale_combo_box.addItem(text)
            self.locale_combo_box.setItemData(i, lang)
        self.retranslateUi(self)
        self.setWindowTitle(self.windowTitle() + ' v.' + __version__)

        self.last_units = copy.copy(self.units)
        self.prev_units = copy.copy(self.units)
        self.norma_original_value = 0
        self.socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM)]

        logger.info(self.alive_sensors)
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
        self.open_generator_button.setEnabled(False)
        self.open_button.pressed.connect(self.open_session)
        self.connection_settings_button.pressed.connect(self.open_connections_settings)
        self.norma_checkbox.stateChanged.connect(self.norma_checked)
        self.dark_theme_checkbox.stateChanged.connect(self.change_theme)
        self.slide_window_time_spinbox.setMaximum(999)
        self.slide_window_time_spinbox.valueChanged.connect(self.change_sliding_window_size)
        self.norma_val_spinbox.valueChanged.connect(self.norma_checked)
        self.copy_graph_button.pressed.connect(self.copy_image)
        self.units_rbutton1.clicked.connect(self.update_units)
        self.units_rbutton2.clicked.connect(self.update_units)
        self.units_rbutton3.clicked.connect(self.update_units)
        self.locale_combo_box.currentIndexChanged.connect(self.change_locale)
        self.tittle_line_edit.textChanged.connect(self.set_title)
        self.copy_data_button.pressed.connect(self.copy_data)
        self.measure_interval_line_edit.valueChanged.connect(self.set_measure_interval)

        self.groupBox_8.setVisible(False)
        self.s1_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s2_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s3_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s4_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s5_legend_checkbox.stateChanged.connect(self.hide_line_plot)

        self.marker_checkbox.stateChanged.connect(self.on_off_markers)

        self.data_update_timer = QtCore.QTimer()
        self.update_period = 1000
        self.data_update_timer.setInterval(self.update_period)
        self.data_update_timer.timeout.connect(self.read_probe_data)

        if not self.search_config_file():
            logger.warning("Config file does not exist. Set default settings")
            self.config_obj = Config()
            create_json_file(self.config_obj, self.config_file_name)

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
            self.connections_settings_widget.accept_button.pressed.connect(self.accept_connection_settings)
        else:
            logger.info("Config exists. Settings loaded from file")
            try:
                with open(self.config_file_name, "r+", encoding='utf8') as read_file:
                    self.config_obj = Config()
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
                    self.last_units = copy.copy(self.units)
                    self.prev_units = copy.copy(self.units)
                    self.update_units(self.units)
                    self.norma_val_spinbox.setValue(self.config_obj.norma_val)
                    self.norma_checkbox.setChecked(self.config_obj.norma)

                    if self.config_obj.theme == 'dark':
                        self.dark_theme_checkbox.setChecked(True)
                        self.change_theme(state=True)

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
                    self.connections_settings_widget.accept_button.pressed.connect(self.accept_connection_settings)

                    self.send_all_sensors_parallel(self.threads, self.connect)

            except Exception as error:
                logger.error(error)

        self.set_enable_sensors_checkbox()

        with open('config.json', 'r+', encoding='utf8') as f:
            d = json.load(f)
            logger.info(json.dumps(d, indent=4, sort_keys=True))

    @staticmethod
    def connect(sock, ip, port):
        try:
            logger.info('trying to connect to ' + str(ip) + ':' + str(port))
            sock.connect((ip, port))
            sock.settimeout(2)
            return read_sensor_ident(sock)
        except Exception as ex:
            logger.error(ex)
            return False

    @staticmethod
    def disconnect(sock):
        sock.close()
        logger.info(str(sock) + ' disconnected')
        return False

    def update_sensors(self):
        if self.connections_settings_widget.server_ip_line_edit.text() == '':
            if self.current_locale == 'ru':
                answer = QMessageBox.information(self, 'Внимание!',
                                                 "Не указан IP сервера.\nУкажите IP в пункте \"Настройки подключения\"",
                                                 QMessageBox.Ok, QMessageBox.Ok)
            else:
                answer = QMessageBox.information(self, 'Warning!',
                                                 "Ip did not set.\nSet server Ip address in \"Connection settings\"",
                                                 QMessageBox.Ok, QMessageBox.Ok)
            if answer:
                self.session_settings_widget.raise_()
            return
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
                                                   name='sensor ' + str(i) + ' thread')
            else:
                threads[i] = ThreadWithReturnValue(target=function, args=[sock],
                                                   name='sensor ' + str(i) + ' thread')
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
            logger.info(file_full_path)
            log = pd.read_csv(file_full_path, sep=';', decimal=',')
            logger.info(list(log))
            if 'Time' in log:
                self.viewer = SessionViewer(data=log)
                self.viewer.viewer_custom_plot.pgcustom.change_locale(self.current_locale)
                self.change_plot_locale(self.locale_combo_box.currentIndex())
                self.viewer.current_locale = self.current_locale
                self.viewer.show()
                self.viewer.setWindowIcon(QtGui.QIcon('smef/icon/engeneering.ico'))
                if self.dark_theme_checkbox.isChecked():
                    self.viewer.viewer_custom_plot.pgcustom.set_theme('dark')
                else:
                    self.viewer.viewer_custom_plot.pgcustom.set_theme('light')
            else:
                logger.error('Incorrect log file' + str(file_full_path))
                QMessageBox.warning(self, 'Внимание!', "Выбран некорректный файл лога.", QMessageBox.Ok, QMessageBox.Ok)
                return

    def send_to_connected_sensors(self, sock, threads):
        fields = [[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]]
        for s in [i for i, x in enumerate(self.alive_sensors) if x]:
            # fields[i] = read_single_probe(sock)
            threads[s] = ThreadWithReturnValue(target=read_single_probe, args=[sock[s]], name='sensor ' + str(s) + ' thread')
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
        # self.customplot.pgcustom.update_plot_data()

        if self.log_checkbox.isChecked():
            try:
                with open(self.session_settings_widget.path_line_edit.text() + '/' +
                          self.session_settings_widget.filename_line_edit.text() + '.csv', 'a+') as log:
                    log_string = str(time.time()).replace('.', ',') + ';' + \
                                 str(time.strftime("%H:%M:%S \\ %d.%m.%Y")) + ';'
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
                logger.error('Write log file error:' + str(ex))
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

        self.customplot.pgcustom.update_plot_data(self.units_mode)
        app.processEvents()
        return fields

    def new_session(self):
        self.session_settings_widget.show()

    def start_plot(self):
        self.stop_button.setEnabled(True)

        if self.graph_start_button.text() in ['Старт', 'Start']:
            self.data_update_timer.start(self.update_period)
            self.customplot.pgcustom.start()
            if self.current_locale == 'ru':
                self.graph_start_button.setText('Пауза')
            else:
                self.graph_start_button.setText('Pause')
        elif self.graph_start_button.text() in ['Пауза', 'Pause']:
            self.customplot.pgcustom.stop()
            self.data_update_timer.stop()
            if self.current_locale == 'ru':
                self.graph_start_button.setText('Старт')
            else:
                self.graph_start_button.setText('Start')

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

    def copy_image(self):
        try:
            if not os.path.isdir(self.images_folder):
                logger.info('Create new images folder' + str(self.images_folder))
                os.mkdir(self.images_folder)
            else:
                logger.info('Images folder exists')
            file_name = datetime.datetime.now().strftime("/%d.%m.%y-%H_%M_%S") + ".png"
            exporter = pg.exporters.ImageExporter(self.customplot.pgcustom.plotItem)
            url = QtCore.QUrl.fromLocalFile(self.images_folder + file_name)
            logger.info(url)
            data = QtCore.QMimeData()
            data.setUrls([url])
            self.app.clipboard().setMimeData(data)
            exporter.export(self.images_folder + file_name)
            # os.remove('x:/SMEP/' + file_name)

        except Exception as ex:
            logger.error(ex)

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
        # log = pd.concat([self.df, pd.DataFrame({'----': ['']*5}),
        #                  pd.DataFrame({'': ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5']}),
        #                  self.table,
        #                  pd.DataFrame({'norma': [self.norma_val_spinbox.value()]}),
        #                  pd.DataFrame({'units': [self.units]})], axis=1)

    def change_sliding_window_size(self):
        val = self.slide_window_time_spinbox.value() * 3600 // self.measure_interval_line_edit.value()
        self.customplot.pgcustom.sliding_window_size = val
        if len(self.customplot.pgcustom.data[0]) > 0:
            self.customplot.pgcustom.data = \
                self.customplot.pgcustom.data[:, -self.customplot.pgcustom.sliding_window_size:]

    def set_measure_interval(self):
        self.update_period = self.measure_interval_line_edit.value() * 1000
        self.data_update_timer.setInterval(self.update_period)
        self.slide_window_time_spinbox.setValue(self.customplot.pgcustom.sliding_window_size // 3600 *
                                                self.measure_interval_line_edit.value())
        self.change_sliding_window_size()

    def update_units(self, units=None):
        if units is None:  # after radioButton clicked
            try:
                if self.sender().text() != self.units:
                    convert_to_log = lambda x: 20 * np.log10(x * 10**6)
                    if self.units_rbutton1.isChecked():
                        self.last_units = copy.copy(self.units)

                        self.customplot.pgcustom.convert_plot_data(mode=0)
                        self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                        self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                        if self.current_locale == 'ru':
                            self.units = 'В/м'
                            self.customplot.pgcustom.left_axis.labelUnits = "В/м"
                        else:
                            self.units = 'V/m'
                            self.customplot.pgcustom.left_axis.labelUnits = "V/m"
                        self.customplot.pgcustom.left_axis.label.setHtml(self.customplot.pgcustom.left_axis.labelString())

                        if self.last_units in ['дБмкВ/м', 'dBµV/m']:
                            self.norma_val_spinbox.setValue(reverse_convert(self.norma_val_spinbox.value(), mode=2))
                        elif self.last_units in ['Вт/м²', 'W/m²']:
                            self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() * 377)
                        else:
                            raise Exception

                        self.units_mode = 0
                    if self.units_rbutton2.isChecked():
                        self.last_units = copy.copy(self.units)
                        if self.current_locale == 'ru':
                            self.units = 'дБмкВ/м'
                            self.customplot.pgcustom.left_axis.labelUnits = "дБмкВ/м"
                        else:
                            self.units = 'dBµV/m'
                            self.customplot.pgcustom.left_axis.labelUnits = 'dBµV/m'
                        self.customplot.pgcustom.left_axis.label.setHtml(self.customplot.pgcustom.left_axis.labelString())
                        if self.norma_val_spinbox.value() <= 0:
                            self.norma_val_spinbox.setValue(0.001)
                        if self.last_units in ['В/м', 'V/m']:
                            self.norma_val_spinbox.setValue(convert_to_log(self.norma_val_spinbox.value()))
                        elif self.last_units in ['Вт/м²', 'W/m²']:
                            self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() * 377)
                            self.norma_val_spinbox.setValue(convert_to_log(self.norma_val_spinbox.value()))
                        else:
                            raise Exception
                        try:
                            self.customplot.pgcustom.convert_plot_data(mode=1)
                        except Exception as ex:
                            logger.error(ex)
                        self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                        self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                        self.units_mode = 1
                    if self.units_rbutton3.isChecked():
                        self.last_units = copy.copy(self.units)
                        self.customplot.pgcustom.enableAutoRange(axis='y', enable=True)
                        self.customplot.pgcustom.enableAutoRange(axis='x', enable=True)
                        if self.current_locale == 'ru':
                            self.units = 'Вт/м²'
                            self.customplot.pgcustom.left_axis.labelUnits = "Вт/м²"
                        else:
                            self.units = 'W/m²'
                            self.customplot.pgcustom.left_axis.labelUnits = "W/m²"
                        self.customplot.pgcustom.left_axis.label.setHtml(self.customplot.pgcustom.left_axis.labelString())
                        if self.last_units in ('дБмкВ/м', 'dBµV/m'):
                            self.norma_val_spinbox.setValue(reverse_convert(self.norma_val_spinbox.value(), mode=2))
                            self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() / 377)
                        elif self.last_units in ('В/м', 'V/m'):
                            self.norma_val_spinbox.setValue(self.norma_val_spinbox.value() / 377)
                        else:
                            raise Exception
                        try:
                            self.customplot.pgcustom.convert_plot_data(mode=2)
                        except Exception as ex:
                            logger.error(ex)
                        self.units_mode = 2
                    self.norma_unit_label.setText(self.units)
            except Exception as ex:
                print(ex)
                logger.error(ex)
        else:  # after load config file
            if units in ['В/м', 'V/m']:
                self.units_rbutton1.setChecked(True)
                if self.current_locale == 'ru':
                    self.units = 'В/м'
                else:
                    self.units = 'V/m'
                self.units_mode = 0
            elif units in ['дБмкВ/м', 'dBµV/m']:
                self.units_rbutton2.setChecked(True)
                if self.current_locale == 'ru':
                    self.units = 'дБмкВ/м'
                else:
                    self.units = 'dBµV/m'
                self.units_mode = 1
            elif units in ['Вт/м²', 'W/m²']:
                self.units_rbutton3.setChecked(True)
                if self.current_locale == 'ru':
                    self.units = 'Вт/м²'
                else:
                    self.units = 'W/m²'
                self.units_mode = 2
            self.update_units()

    def set_title(self):
        new_tittle = self.tittle_line_edit.text()
        item = self.customplot.pgcustom.getPlotItem()
        if self.dark_theme_checkbox.isChecked():
            item.setTitle("<span style=\"color:white;font-size:30px\">" + new_tittle + "</span>")
        else:
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
                self.s1_legend_checkbox.setChecked(True)
            if self.session_settings_widget.s2_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[1] = True
                self.s2_legend_checkbox.setChecked(True)
            if self.session_settings_widget.s3_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[2] = True
                self.s3_legend_checkbox.setChecked(True)
            if self.session_settings_widget.s4_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[3] = True
                self.s4_legend_checkbox.setChecked(True)
            if self.session_settings_widget.s5_checkbox.isChecked():
                self.sensors_amount += 1
                self.active_sensors[4] = True
                self.s5_legend_checkbox.setChecked(True)
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
        if self.graph_start_button.text() == ('Пауза' or 'Pause'):
            self.customplot.pgcustom.stop()
            self.data_update_timer.stop()
            if self.current_locale == 'ru':
                self.graph_start_button.setText('Старт')
            else:
                self.graph_start_button.setText('Start')
        if self.current_locale == 'ru':
            QMessageBox.information(self, 'Сеанс завершен', "Данные по этому сеансу находятся в папке\n" +
                                    self.session_settings_widget.path_line_edit.text(), QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.information(self, 'Session has finished', "The data for this session is located in the folder:\n" +
                                    self.session_settings_widget.path_line_edit.text(), QMessageBox.Ok, QMessageBox.Ok)
        self.graph_start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def change_locale(self, index):
        data = self.locale_combo_box.itemData(index)
        if data:
            self.trans.load(data)
            self.session_settings_widget.trans.load(data)
            self.connections_settings_widget.trans.load(data)
            if self.viewer is not None:
                self.viewer.trans.load(data)
                self.viewer.current_locale = self.current_locale
            QtWidgets.QApplication.instance().installTranslator(self.trans)
        else:
            QtWidgets.QApplication.instance().removeTranslator(self.trans)
        self.change_plot_locale(index)

    def change_plot_locale(self, index):
        if index:
            self.current_locale = 'en'
            self.units = self.get_translated_units()
            self.customplot.pgcustom.english_labels['units'] = self.units
            self.customplot.pgcustom.change_locale('en')
            if self.viewer is not None:
                self.viewer.current_locale = self.current_locale
                self.viewer.units_update()
                self.viewer.viewer_custom_plot.pgcustom.change_locale(self.current_locale)
                self.viewer.viewer_custom_plot.pgcustom.legend.clear()
                for i, val in enumerate(self.viewer.connected_sensors):
                    if val:
                        self.viewer.viewer_custom_plot.pgcustom.legend.addItem(
                            self.viewer.viewer_custom_plot.pgcustom.data_line[i],
                            self.viewer.viewer_custom_plot.pgcustom.english_labels.get('legend') + str(i + 1))
        else:
            self.current_locale = 'ru'
            self.units = self.get_translated_units()
            self.customplot.pgcustom.russian_labels['units'] = self.units
            self.customplot.pgcustom.change_locale('ru')
            if self.viewer is not None:
                self.viewer.current_locale = self.current_locale
                self.viewer.units_update()
                self.viewer.viewer_custom_plot.pgcustom.change_locale(self.current_locale)
                self.viewer.viewer_custom_plot.pgcustom.legend.clear()
                for i, val in enumerate(self.viewer.connected_sensors):
                    if val:
                        self.viewer.viewer_custom_plot.pgcustom.legend.addItem(
                            self.viewer.viewer_custom_plot.pgcustom.data_line[i],
                            self.viewer.viewer_custom_plot.pgcustom.russian_labels.get('legend') + str(i + 1))

    def get_translated_units(self):
        if self.units_rbutton1.isChecked():
            if self.current_locale == 'ru':
                return 'В/м'
            else:
                return 'V/m'
        elif self.units_rbutton2.isChecked():
            if self.current_locale == 'ru':
                return 'дБмкВ/м'
            else:
                return 'dBµV/m'
        elif self.units_rbutton3.isChecked():
            if self.current_locale == 'ru':
                return 'Вт/м²'
            else:
                return 'W/m²'

        # if units == 'В/м':
        #     return 'V/m'
        # elif units == 'дБмкВ/м':
        #     return 'dBµV/m'
        # elif units == 'Вт/м²':
        #     return 'W/m²'
        #
        # elif units == 'V/m':
        #     return 'В/м'
        # elif units == 'dBµV/m':
        #     return 'дБмкВ/м'
        # elif units == 'W/m²':
        #     return 'Вт/м²'
        else:
            raise Exception

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
            self.setWindowTitle(self.windowTitle() + ' v.' + __version__)
        super(MainWindow, self).changeEvent(event)
        try:
            self.norma_unit_label.setText(self.units)
        except Exception as ex:
            logger.warning(ex)

    def accept_connection_settings(self):
        logger.info('new server IP:' + self.connections_settings_widget.server_ip_line_edit.text())
        self.server_ip = self.connections_settings_widget.server_ip_line_edit.text()
        with open('config.json') as f:
            config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
            config.terminal_server_ip = self.server_ip
        with open('config.json', 'w') as f:
            f.write(json.dumps(config, default=lambda o: o.__dict__, sort_keys=True, indent=4))
        self.update_sensors()
        self.connections_settings_widget.close()

    def hide_line_plot(self):
        try:
            self.customplot.pgcustom.data_line[0].setVisible(self.s1_legend_checkbox.isChecked())
            self.customplot.pgcustom.data_line[1].setVisible(self.s2_legend_checkbox.isChecked())
            self.customplot.pgcustom.data_line[2].setVisible(self.s3_legend_checkbox.isChecked())
            self.customplot.pgcustom.data_line[3].setVisible(self.s4_legend_checkbox.isChecked())
            self.customplot.pgcustom.data_line[4].setVisible(self.s5_legend_checkbox.isChecked())
            self.customplot.pgcustom.legend.update()
        except Exception as ex:
            logger.error(ex)
            logger.warning('Probably started new session while current session in process')

    def on_off_markers(self, state):
        if state:
            self.customplot.pgcustom.display_data_under_mouse = True
            self.customplot.pgcustom.cursor_vLine.setVisible(True)
            self.customplot.pgcustom.cursor_hLine.setVisible(True)
            self.customplot.pgcustom.marker_label.setVisible(True)
        else:
            self.customplot.pgcustom.display_data_under_mouse = False
            self.customplot.pgcustom.cursor_vLine.setVisible(False)
            self.customplot.pgcustom.cursor_hLine.setVisible(False)
            self.customplot.pgcustom.marker_label.setVisible(False)

    def change_theme(self, state):
        if state:
            theme = 'dark'
            app.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette, qt_api='pyqt5'))
            self.customplot.pgcustom.set_theme(theme)
            if self.viewer is not None:
                self.viewer.viewer_custom_plot.pgcustom.set_theme(theme)
                self.viewer.set_title()
        else:
            theme = 'light'
            app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette, qt_api='pyqt5'))
            self.customplot.pgcustom.set_theme(theme)
            if self.viewer is not None:
                self.viewer.viewer_custom_plot.pgcustom.set_theme(theme)
                self.viewer.set_title()
        self.set_title()
        with open('config.json') as f:
            config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
            config.theme = theme
        with open('config.json', 'w') as f:
            f.write(json.dumps(config, default=lambda o: o.__dict__, sort_keys=True, indent=4))


def main():
    logger.info("Start application")
    global app
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__) + '/icon/engeneering.ico'))
    app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette, qt_api='pyqt5'))

    w = MainWindow()
    w.show()

    app.exec_()
    logger.warning('Stop application')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SMEF client')
    parser.add_argument('-d', '--demo', help='start program with demo server',  action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    if args.demo:
        print('Starting demo server')
        server = DemoServer(debug_print=False)
        server.start_server()
        main()
    else:
        print('Starting without demo server')
        main()
