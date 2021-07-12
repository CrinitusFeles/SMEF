import socket
import os
from tabulate import tabulate
import pandas as pd
import subprocess
import sys
import openpyxl
import time
import pyqtgraph as pg
from pyqtgraph import InfiniteLine
import pyqtgraph.exporters
from pyperclip import copy, paste
import datetime
from shutil import copyfile
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5 import QtCore, QtGui, QtTest, QtWidgets
import mainwindow
import select
import numpy as np
import re
import generator_window
import new_session_window

host = "10.6.1.95"
port1 = 4001


def ping():
    out, error = subprocess.Popen(["ping", "-l", "1", host], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()
    answer = out.decode('IBM866')
    if answer[-14:-10] == '100%':
        print('connection lost')
    else:
        print('connection OK')


class GeneratorSettings(QWidget, generator_window.Ui_generator_settings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Настройки генератора')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)

    def accept_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.close()


class NewSession(QWidget, new_session_window.Ui_new_session_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Новый сеанс')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.path_tool_button.pressed.connect(self.open_file_system)

        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)

    def accept_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.close()

    def open_file_system(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        file_dialog.open()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_full_path = str(file_dialog.selectedFiles()[0])
            self.path_line_edit.setText(file_full_path)
            # self.customplot.pgcustom.clear_plot()
            # self.plot_from_file(file_full_path)


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("СМЭП КЛИЕНТ")
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.connect((host, port1))
        # self.sock.settimeout(1)
        self.generator_settings_widget = GeneratorSettings()
        self.session_settings_widget = NewSession()
        df = None

        self.start_button.pressed.connect(self.new_session)
        self.graph_start_button.pressed.connect(self.start_plot)
        self.open_generator_button.pressed.connect(self.open_generator_settings)
        self.open_button.pressed.connect(self.open_session)
        self.checkBox_6.stateChanged.connect(self.norma_checked)
        self.slide_window_time_spinbox.valueChanged.connect(self.change_sliding_window_size)
        self.norma_val_spinbox.valueChanged.connect(self.norma_checked)
        self.copy_graph_button.pressed.connect(self.copy_image)
        self.units_rbutton1.toggled.connect(self.update_units)
        self.units_rbutton2.toggled.connect(self.update_units)
        self.units_rbutton3.toggled.connect(self.update_units)
        self.tittle_line_edit.textChanged.connect(self.set_title)
        self.copy_data_button.pressed.connect(self.copy_data)

        self.data_update_timer = QtCore.QTimer()
        self.data_update_timer.timeout.connect(self.read_probe_data)

    def open_generator_settings(self):
        self.generator_settings_widget.show()

    def open_session(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.open()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_full_path = str(file_dialog.selectedFiles()[0])
            # self.path_line_edit.setText(file_full_path)

    def disconnect_device(self):
        self.sock.close()

    def read_ident(self):
        answer = ''
        data_counter = 0
        self.sock.send('*IDN?\r'.encode())
        try:
            while True:
                data = self.sock.recv(1024)
                answer += data.decode()
                data_counter += 1
                if data == b'\r':
                    break
            print(answer)
        except Exception as ex:
            print(answer, data_counter)
            print(ex)

    def read_probe_data(self):
        answer = ''
        bytes_array = b''
        data_counter = 0
        fields = [0, 0, 0, 0]
        try:
            self.sock.send('D\r'.encode())
            while True:
                data = self.sock.recv(2048)
                bytes_array += data
                answer += data.decode()
                data_counter += 1
                if data_counter == 14:
                    break
            print(answer)
            fields = [float(x) for x in re.findall(r'\d{2}\.{1}\d{2}', answer)]
            print(fields)
            self.x_label.setText(str(fields[0]))
            self.y_label.setText(str(fields[1]))
            self.z_label.setText(str(fields[2]))
            self.customplot.pgcustom.sensor1 = fields[3]
            self.customplot.pgcustom.update_plot_data()
        except Exception as ex:
            print(answer, data_counter)
            print(bytes_array)
            print(ex)
        return fields

    def new_session(self):
        self.session_settings_widget.show()

    def start_plot(self):
        if self.graph_start_button.text() == 'Старт':
            self.data_update_timer.start(300)
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
        state = self.checkBox_6.checkState()
        if self.customplot.pgcustom.infinit_line is not None:
            self.customplot.pgcustom.removeItem(self.customplot.pgcustom.infinit_line)
            self.customplot.pgcustom.infinite_line = None
        if state == 2:
            self.customplot.pgcustom.infinit_line = self.customplot.pgcustom.addLine(
                x=None, y=val, pen=pg.mkPen('r', width=3), label='                                                     '
                                                                 '                                                     '
                                                                 '     norma')
        else:
            self.customplot.pgcustom.removeItem( self.customplot.pgcustom.infinit_line)
            self.customplot.pgcustom.infinit_line = None
            print(self.customplot.pgcustom.infinit_line is None)
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
            file_name = datetime.datetime.now().strftime("%d.%m.%y-%H_%M_%S") + ".png"
            exporter = pg.exporters.ImageExporter(self.customplot.pgcustom.plotItem)
            url = QtCore.QUrl.fromLocalFile('x:/SMEP/' + file_name)
            print(url)
            data = QtCore.QMimeData()
            data.setUrls([url])
            app.clipboard().setMimeData(data)
            exporter.export(file_name)
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
        print(self.df.to_markdown())
        self.df.to_clipboard()

    def change_sliding_window_size(self):
        val = self.slide_window_time_spinbox.value() * 60
        self.customplot.pgcustom.sliding_window_size = val

    def update_units(self):
        try:
            if self.units_rbutton1.isChecked():
                state = 'В/м'
                self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(False)
            elif self.units_rbutton2.isChecked():
                state = 'дБмкВ/м'
                self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(True)
            else:
                state = 'Вт/м2'
                self.customplot.pgcustom.getPlotItem().getAxis('left').setLogMode(False)
            self.norma_unit_label.setText(state)
        except Exception as ex:
            print(ex)

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

    def export_data(self):
        try:
            if self.session_settings_widget.xlsx_checkbox.isChecked():
                self.df.to_excel('output.xlsx')
            elif self.session_settings_widget.csv_checkbox.isChecked():
                self.df.to_csv('output.csv')
            elif self.session_settings_widget.md_checkbox.isChecked():
                self.df.to_csv('output.md')
            elif self.session_settings_widget.html_checkbox.isChecked():
                self.df.to_csv('output.html')
            elif self.session_settings_widget.txt_checkbox.isChecked():
                self.df.to_csv(r'output.txt', header=None, sep=' ', mode='a')
            elif self.session_settings_widget.tex_checkbox.isChecked():
                self.df.to_latex('output.tex')
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon2.ico'))

    w = MainWindow()
    w.setWindowIcon(QtGui.QIcon('icon2.ico'))
    w.show()

    app.exec_()
