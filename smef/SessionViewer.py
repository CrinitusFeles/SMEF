import copy
import pyqtgraph.exporters
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem
try:
    from .session_viewer import *
    from .app_logger import *
    from .double_range_slider import *
    from .utils import *
except Exception as ex:
    from session_viewer import *
    from app_logger import *
    from double_range_slider import *
    from utils import *

logger = get_logger(__name__)


class SessionViewer(QWidget, Ui_session_viewer):
    def __init__(self, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Просмотр сеанса')
        self.setWindowIcon(QtGui.QIcon('./icon/engeneering.ico'))

        self.viewer_tittle_line_edit.textChanged.connect(self.set_title)

        self.app = [x.app for x in QApplication.topLevelWidgets() if x.objectName() == 'MainWindow'][0]

        self.trans = QtCore.QTranslator(self)
        self.retranslateUi(self)

        self.viewer_copy_data_button.pressed.connect(self.copy_data)
        self.viewer_copy_graph_button.pressed.connect(self.copy_image)
        self.viewer_norma_checkbox.stateChanged.connect(self.norma_checked)
        self.viewer_norma_val_spinbox.valueChanged.connect(self.norma_checked)
        self.units_rbutton1.clicked.connect(self.units_update)
        self.units_rbutton2.clicked.connect(self.units_update)
        self.units_rbutton3.clicked.connect(self.units_update)

        self.groupBox_3.setVisible(False)
        self.s1_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.checkBos2_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s3_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s4_legend_checkbox.stateChanged.connect(self.hide_line_plot)
        self.s5_legend_checkbox.stateChanged.connect(self.hide_line_plot)

        self.marker_checkbox.stateChanged.connect(self.on_off_markers)

        self.slider = QRangeSlider()
        # self.slider.show()
        self.slider.setRange(0, 100)
        self.slider.startValueChanged.connect(self.update_plot)
        self.slider.endValueChanged.connect(self.update_plot)
        self.slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.slider.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.slider.setDrawValues(False)
        # QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved(int)'), echo)
        # self.slider.show()
        # self.slider.raise_()
        self.current_locale = 'ru'

        self.units = 'В/м'
        self.units_mode = 0
        self.viewer_vertical_layout.addWidget(self.slider)
        self.connected_sensors = [False, False, False, False, False]
        self.data = kwargs.get('data', None)
        self.header = list(self.data)[1:]
        self.time = self.data['Time']
        del self.data['Time']
        self.description = ''
        self.minmax = None

        if self.header[-1].find('Sensor') == -1:
            self.description = self.header[-1]
            del self.data[self.header[-1]]
            self.session_description_browser.setText(self.description)

        for header in self.header:
            if header == 'Sensor1':
                self.connected_sensors[0] = True
                self.s1_legend_checkbox.setChecked(True)
            elif header == 'Sensor2':
                self.connected_sensors[1] = True
                self.checkBos2_legend_checkbox.setChecked(True)
            elif header == 'Sensor3':
                self.connected_sensors[2] = True
                self.s3_legend_checkbox.setChecked(True)
            elif header == 'Sensor4':
                self.connected_sensors[3] = True
                self.s4_legend_checkbox.setChecked(True)
            elif header == 'Sensor5':
                self.connected_sensors[4] = True
                self.s5_legend_checkbox.setChecked(True)

        logger.info('connected sensors:' + str(self.connected_sensors))

        self.np_data = self.data.T.to_numpy()
        # self.viewer_norma_checkbox.setChecked(True)
        self.viewer_norma_val_spinbox.setValue(kwargs.get('norma_val', 0))

        # print(self.data)
        self.get_connected_sensors()
        self.indices = [i for i, x in enumerate(self.connected_sensors) if x]
        self.viewer_custom_plot.pgcustom.legend.clear()
        self.data_len = len(self.np_data[0])
        self.viewer_custom_plot.pgcustom.setLimits(yMin=-10000, yMax=10000, xMin=self.np_data[0][0] - 50000,
                                                   xMax=self.np_data[0][-1] + 50000)
        self.viewer_custom_plot.pgcustom.original_data = self.np_data
        self.viewer_custom_plot.pgcustom.data = self.np_data
        self.update_viewer(init_flag=True)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
        super(SessionViewer, self).changeEvent(event)

    def update_viewer(self, init_flag=False):
        if self.data is not None:
            for i in range(len(self.np_data) - 1):
                if self.np_data[i+1] is not None:
                    # boolean mask for self.viewer_custom_plot.pgcustom.data_line array
                    [b for a, b in zip(self.connected_sensors, self.viewer_custom_plot.pgcustom.data_line) if a][i].setData(self.np_data[0], self.np_data[i+1])
                    if init_flag:
                        self.viewer_custom_plot.pgcustom.legend.addItem(self.viewer_custom_plot.pgcustom.data_line[self.indices[i]], "Датчик " + str(self.indices[i] + 1))
                    # self.viewer_custom_plot.pgcustom.data_line[i].setData(np_data[0], np_data[i+1])
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
            self.app.processEvents()
        else:
            logger.info('empty data')

        self.minmax = np.column_stack((np.amin(self.np_data[1:], axis=1), np.mean(self.np_data[1:], axis=1),
                                       np.amax(self.np_data[1:], axis=1)))

        self.update_table()

    def units_update(self):
        try:
            if self.sender().text() != self.units:
                convert_to_log = lambda x: 20 * np.log10(x * 10**6)
                if self.units_rbutton1.isChecked():
                    self.last_units = copy.copy(self.units)
                    # self.viewer_custom_plot.pgcustom.convert_plot_data(mode=0)

                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
                    if self.current_locale == 'ru':
                        self.units = 'В/м'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "В/м"
                        self.viewer_custom_plot.pgcustom.russian_labels['units'] = "В/м"
                    else:
                        self.units = 'V/m'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "V/m"
                        self.viewer_custom_plot.pgcustom.english_labels['units'] = "V/m"
                    self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())

                    if self.last_units in ['дБмкВ/м', 'dBµV/m']:
                        self.viewer_norma_val_spinbox.setValue(reverse_convert(self.viewer_norma_val_spinbox.value(), mode=2))
                    elif self.last_units in ['Вт/м²', 'W/m²']:
                        self.viewer_norma_val_spinbox.setValue(self.viewer_norma_val_spinbox.value() * 377)
                    else:
                        raise Exception

                if self.units_rbutton2.isChecked():
                    self.last_units = copy.copy(self.units)
                    if self.current_locale == 'ru':
                        self.units = 'дБмкВ/м'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "дБмкВ/м"
                        self.viewer_custom_plot.pgcustom.russian_labels['units'] = "дБмкВ/м"
                    else:
                        self.units = 'dBµV/m'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "dBµV/m"
                        self.viewer_custom_plot.pgcustom.english_labels['units'] = "dBµV/m"
                    self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())
                    if self.viewer_norma_val_spinbox.value() <= 0:
                        self.viewer_norma_val_spinbox.setValue(0.001)
                    if self.last_units in ['В/м', 'V/m']:
                        self.viewer_norma_val_spinbox.setValue(convert_to_log(self.viewer_norma_val_spinbox.value()))
                    elif self.last_units in ['Вт/м²', 'W/m²']:
                        self.viewer_norma_val_spinbox.setValue(self.viewer_norma_val_spinbox.value() * 377)
                        self.viewer_norma_val_spinbox.setValue(convert_to_log(self.viewer_norma_val_spinbox.value()))
                    else:
                        raise Exception
                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
                if self.units_rbutton3.isChecked():
                    self.last_units = copy.copy(self.units)
                    # self.viewer_custom_plot.pgcustom.convert_plot_data(mode=2)
                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
                    self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
                    if self.current_locale == 'ru':
                        self.units = 'Вт/м²'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "Вт/м²"
                        self.viewer_custom_plot.pgcustom.russian_labels['units'] = "Вт/м²"
                    else:
                        self.units = 'W/m²'
                        self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "W/m²"
                        self.viewer_custom_plot.pgcustom.english_labels['units'] = "W/m²"
                    self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())
                    if self.last_units in ('дБмкВ/м', 'dBµV/m'):
                        self.viewer_norma_val_spinbox.setValue(reverse_convert(self.viewer_norma_val_spinbox.value(), mode=2))
                        self.viewer_norma_val_spinbox.setValue(self.viewer_norma_val_spinbox.value() / 377)
                    elif self.last_units in ('В/м', 'V/m'):
                        self.viewer_norma_val_spinbox.setValue(self.viewer_norma_val_spinbox.value() / 377)
                    else:
                        raise Exception
                self.viewer_norma_unit_label.setText(self.units)
                self.viewer_custom_plot.pgcustom.change_locale(self.current_locale)
        except Exception as ex:
            logger.error(ex)

        if self.units_rbutton1.isChecked():
            # self.viewer_custom_plot.pgcustom.convert_plot_data(mode=0)
            self.np_data = np.copy(self.viewer_custom_plot.pgcustom.original_data)
            self.viewer_custom_plot.pgcustom.data = self.np_data
            self.update_viewer()

            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
            if self.current_locale == 'ru':
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "В/м"
                self.viewer_norma_unit_label.setText("В/м")
            else:
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "V/m"
                self.viewer_norma_unit_label.setText("V/m")
            self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())
            # self.norma_val_spinbox.setValue(utils.converter(self.norma_val_spinbox.value(), mode=0))
            # utils.converter(self.norma_val_spinbox.value(), mode=0)
        if self.units_rbutton2.isChecked():
            self.np_data = np.copy(self.viewer_custom_plot.pgcustom.original_data)
            self.np_data[1:, ] = converter(self.np_data[1:, ], mode=1)
            self.viewer_custom_plot.pgcustom.data = self.np_data
            self.update_viewer()
            # self.viewer_custom_plot.pgcustom.convert_plot_data(mode=1)
            if self.current_locale == 'ru':
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "дБмкВ/м"
                self.viewer_norma_unit_label.setText("дБмкВ/м")
            else:
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "dBµV/m"
                self.viewer_norma_unit_label.setText("dBµV/m")
            self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())
            # self.norma_val_spinbox.setValue(utils.converter(self.norma_val_spinbox.value(), mode=1))
            # utils.converter(self.norma_val_spinbox.value(), mode=1)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
        if self.units_rbutton3.isChecked():
            self.np_data = np.copy(self.viewer_custom_plot.pgcustom.original_data)
            self.np_data[1:, ] = converter(self.np_data[1:, ], mode=2)
            self.viewer_custom_plot.pgcustom.data = self.np_data
            self.update_viewer()
            # self.viewer_custom_plot.pgcustom.convert_plot_data(mode=2)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
            if self.current_locale == 'ru':
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "Вт/м²"
                self.viewer_norma_unit_label.setText("Вт/м²")
            else:
                self.viewer_custom_plot.pgcustom.left_axis.labelUnits = "W/m²"
                self.viewer_norma_unit_label.setText("W/m²")
            self.viewer_custom_plot.pgcustom.left_axis.label.setHtml(self.viewer_custom_plot.pgcustom.left_axis.labelString())
            # print(utils.converter(self.norma_val_spinbox.value(), mode=2))
            # self.norma_val_spinbox.setValue(utils.converter(self.norma_val_spinbox.value(), mode=2))

    def update_table(self):
        k = 0
        normalized_minmax = np.array([])
        for i, val in enumerate(self.connected_sensors):
            if val:
                if i == 0:
                    normalized_minmax = self.minmax[0, :].reshape(1, 3)
                else:
                    normalized_minmax = np.append(normalized_minmax, self.minmax[k, :].reshape(1, 3), axis=0)
                k += 1
            else:
                if len(normalized_minmax) == 0:
                    normalized_minmax = np.zeros((1, 3))
                else:
                    normalized_minmax = np.append(normalized_minmax, np.zeros((1, 3)), axis=0)
        for i in range(5):
            if self.connected_sensors[i]:
                for j in range(3):
                    self.viewer_minmax_values_table.setItem(i, j, QTableWidgetItem('{:.2f}'.format(normalized_minmax[i, j])))

    def update_plot(self, value):
        low_range = self.slider.start()
        high_range = self.slider.end()
        for i in range(len(self.np_data) - 1):
            if self.np_data[i+1] is not None:
                # boolean mask for self.viewer_custom_plot.pgcustom.data_line array
                [b for a, b in zip(self.connected_sensors, self.viewer_custom_plot.pgcustom.data_line)
                 if a][i].setData(self.np_data[0][low_range*self.data_len//100:high_range*self.data_len//100],
                                  self.np_data[i+1][low_range*self.data_len//100:high_range*self.data_len//100])

        self.minmax = np.column_stack((np.amin(self.np_data[1:][:, low_range*self.data_len//100:high_range*self.data_len//100], axis=1),
                                    np.mean(self.np_data[1:][:, low_range*self.data_len//100:high_range*self.data_len//100], axis=1),
                                    np.amax(self.np_data[1:][:, low_range*self.data_len//100:high_range*self.data_len//100], axis=1)))

        self.update_table()

    def get_connected_sensors(self):
        header = list(self.data)
        if 'Sensor1' in header:
            self.connected_sensors[0] = True
        if 'Sensor2' in header:
            self.connected_sensors[1] = True
        if 'Sensor3' in header:
            self.connected_sensors[2] = True
        if 'Sensor4' in header:
            self.connected_sensors[3] = True
        if 'Sensor5' in header:
            self.connected_sensors[4] = True

    def set_title(self):
        new_tittle = self.viewer_tittle_line_edit.text()
        item = self.viewer_custom_plot.pgcustom.getPlotItem()
        if self.viewer_custom_plot.pgcustom.theme == 'dark':
            item.setTitle("<span style=\"color:white;font-size:30px\">" + new_tittle + "</span>")
        else:
            item.setTitle("<span style=\"color:black;font-size:30px\">" + new_tittle + "</span>")

    def copy_data(self):
        x1_timestamp = int(self.viewer_custom_plot.pgcustom.visibleRange().getCoords()[0])
        x2_timestamp = int(self.viewer_custom_plot.pgcustom.visibleRange().getCoords()[2])
        data = self.data.copy()
        x = np.array(data['Timestamp'], dtype=int)
        if x1_timestamp < x[0]:
            x1_timestamp = x[0]
        if x2_timestamp > x[-1]:
            x2_timestamp = x[-1]
        data['Timestamp'] = self.time

        slice_data = data.loc[np.where(x == x1_timestamp)[0][0].astype(int):np.where(x == x2_timestamp)[0][0].astype(int)]
        if 'Sensor1' in slice_data:
            slice_data['Sensor1'] = slice_data['Sensor1'].astype(str).str.replace('.', ',', regex=False)
        if 'Sensor2' in slice_data:
            slice_data['Sensor2'] = slice_data['Sensor2'].astype(str).str.replace('.', ',', regex=False)
        if 'Sensor3' in slice_data:
            slice_data['Sensor3'] = slice_data['Sensor3'].astype(str).str.replace('.', ',', regex=False)
        if 'Sensor4' in slice_data:
            slice_data['Sensor4'] = slice_data['Sensor4'].astype(str).str.replace('.', ',', regex=False)
        if 'Sensor5' in slice_data:
            slice_data['Sensor5'] = slice_data['Sensor5'].astype(str).str.replace('.', ',', regex=False)

        slice_data.to_clipboard(index=False)

    def copy_image(self):
        try:
            images_folder = os.getcwd() + '/output/images'
            if not os.path.isdir(images_folder):
                logger.info('Create new images folder:' + str(images_folder))
                os.mkdir(images_folder)
            else:
                logger.info('Images folder exists')
            file_name = datetime.datetime.now().strftime("/%d.%m.%y-%H_%M_%S") + ".png"
            exporter = pg.exporters.ImageExporter(self.viewer_custom_plot.pgcustom.plotItem)
            url = QtCore.QUrl.fromLocalFile(images_folder + file_name)
            print(url)
            data = QtCore.QMimeData()
            data.setUrls([url])
            self.app.clipboard().setMimeData(data)
            exporter.export(images_folder + file_name)
            # os.remove('x:/SMEP/' + file_name)

        except Exception as ex:
            print(ex)

    def norma_checked(self):
        # line = InfiniteLine(pos=1.0, pen=pg.mkPen('r', width=13))
        # self.customplot.pgcustom.addItem(line)
        val = self.viewer_norma_val_spinbox.value()
        state = self.viewer_norma_checkbox.checkState()
        if self.viewer_custom_plot.pgcustom.infinite_line is not None:
            self.viewer_custom_plot.pgcustom.removeItem(self.viewer_custom_plot.pgcustom.infinite_line)
            self.viewer_custom_plot.pgcustom.infinite_line = None
        if state == 2:
            self.viewer_custom_plot.pgcustom.infinite_line = self.viewer_custom_plot.pgcustom.addLine(
                x=None, y=val, pen=pg.mkPen('r', width=3), label='                                                     '
                                                                 '                                                     '
                                                                 '     norma')
        else:
            self.viewer_custom_plot.pgcustom.removeItem(self.viewer_custom_plot.pgcustom.infinite_line)
            self.viewer_custom_plot.pgcustom.infinite_line = None

    def hide_line_plot(self):
        self.viewer_custom_plot.pgcustom.data_line[0].setVisible(self.s1_legend_checkbox.isChecked())
        self.viewer_custom_plot.pgcustom.data_line[1].setVisible(self.checkBos2_legend_checkbox.isChecked())
        self.viewer_custom_plot.pgcustom.data_line[2].setVisible(self.s3_legend_checkbox.isChecked())
        self.viewer_custom_plot.pgcustom.data_line[3].setVisible(self.s4_legend_checkbox.isChecked())
        self.viewer_custom_plot.pgcustom.data_line[4].setVisible(self.s5_legend_checkbox.isChecked())
        self.viewer_custom_plot.pgcustom.legend.update()

    def on_off_markers(self, state):
        if state:
            self.viewer_custom_plot.pgcustom.display_data_under_mouse = True
            self.viewer_custom_plot.pgcustom.cursor_vLine.setVisible(True)
            self.viewer_custom_plot.pgcustom.cursor_hLine.setVisible(True)
            self.viewer_custom_plot.pgcustom.marker_label.setVisible(True)
        else:
            self.viewer_custom_plot.pgcustom.display_data_under_mouse = False
            self.viewer_custom_plot.pgcustom.cursor_vLine.setVisible(False)
            self.viewer_custom_plot.pgcustom.cursor_hLine.setVisible(False)
            self.viewer_custom_plot.pgcustom.marker_label.setVisible(False)