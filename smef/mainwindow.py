# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1307, 857)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setObjectName("start_button")
        self.horizontalLayout_5.addWidget(self.start_button)
        self.open_button = QtWidgets.QPushButton(self.centralwidget)
        self.open_button.setObjectName("open_button")
        self.horizontalLayout_5.addWidget(self.open_button)
        self.open_generator_button = QtWidgets.QPushButton(self.centralwidget)
        self.open_generator_button.setObjectName("open_generator_button")
        self.horizontalLayout_5.addWidget(self.open_generator_button)
        self.connection_settings_button = QtWidgets.QPushButton(self.centralwidget)
        self.connection_settings_button.setObjectName("connection_settings_button")
        self.horizontalLayout_5.addWidget(self.connection_settings_button)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.customplot = CustomPlot(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.customplot.sizePolicy().hasHeightForWidth())
        self.customplot.setSizePolicy(sizePolicy)
        self.customplot.setMinimumSize(QtCore.QSize(0, 400))
        self.customplot.setObjectName("customplot")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.customplot)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4.addWidget(self.customplot)
        self.verticalLayout_7.addLayout(self.verticalLayout_4)
        self.verticalLayout_8.addLayout(self.verticalLayout_7)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.graph_start_button = QtWidgets.QPushButton(self.groupBox_3)
        self.graph_start_button.setObjectName("graph_start_button")
        self.horizontalLayout_7.addWidget(self.graph_start_button)
        self.stop_button = QtWidgets.QPushButton(self.groupBox_3)
        self.stop_button.setObjectName("stop_button")
        self.horizontalLayout_7.addWidget(self.stop_button)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.slide_window_time_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.slide_window_time_spinbox.setMinimum(1)
        self.slide_window_time_spinbox.setMaximum(120)
        self.slide_window_time_spinbox.setProperty("value", 1)
        self.slide_window_time_spinbox.setObjectName("slide_window_time_spinbox")
        self.horizontalLayout.addWidget(self.slide_window_time_spinbox)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.norma_checkbox = QtWidgets.QCheckBox(self.groupBox_5)
        self.norma_checkbox.setObjectName("norma_checkbox")
        self.horizontalLayout_9.addWidget(self.norma_checkbox)
        self.norma_val_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.norma_val_spinbox.setDecimals(4)
        self.norma_val_spinbox.setMinimum(-1000.0)
        self.norma_val_spinbox.setMaximum(1000.0)
        self.norma_val_spinbox.setObjectName("norma_val_spinbox")
        self.horizontalLayout_9.addWidget(self.norma_val_spinbox)
        self.norma_unit_label = QtWidgets.QLabel(self.groupBox_5)
        self.norma_unit_label.setObjectName("norma_unit_label")
        self.horizontalLayout_9.addWidget(self.norma_unit_label)
        self.label_4 = QtWidgets.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_9.addWidget(self.label_4)
        self.marker_checkbox = QtWidgets.QCheckBox(self.groupBox_5)
        self.marker_checkbox.setChecked(True)
        self.marker_checkbox.setObjectName("marker_checkbox")
        self.horizontalLayout_9.addWidget(self.marker_checkbox)
        self.horizontalLayout_2.addWidget(self.groupBox_5)
        self.verticalLayout_8.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_8)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_9 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_9.setObjectName("groupBox_9")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.groupBox_9)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.dark_theme_checkbox = QtWidgets.QCheckBox(self.groupBox_9)
        self.dark_theme_checkbox.setObjectName("dark_theme_checkbox")
        self.horizontalLayout_10.addWidget(self.dark_theme_checkbox)
        self.label_3 = QtWidgets.QLabel(self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_10.addWidget(self.label_3)
        self.locale_combo_box = QtWidgets.QComboBox(self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.locale_combo_box.sizePolicy().hasHeightForWidth())
        self.locale_combo_box.setSizePolicy(sizePolicy)
        self.locale_combo_box.setObjectName("locale_combo_box")
        self.horizontalLayout_10.addWidget(self.locale_combo_box)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem)
        self.horizontalLayout_14.addLayout(self.horizontalLayout_10)
        self.verticalLayout_5.addWidget(self.groupBox_9)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.tittle_line_edit = QtWidgets.QLineEdit(self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tittle_line_edit.sizePolicy().hasHeightForWidth())
        self.tittle_line_edit.setSizePolicy(sizePolicy)
        self.tittle_line_edit.setMinimumSize(QtCore.QSize(320, 0))
        self.tittle_line_edit.setMaximumSize(QtCore.QSize(380, 16777215))
        self.tittle_line_edit.setObjectName("tittle_line_edit")
        self.verticalLayout_9.addWidget(self.tittle_line_edit)
        self.verticalLayout_5.addWidget(self.groupBox_6)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem2)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.minmax_values_table = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.minmax_values_table.sizePolicy().hasHeightForWidth())
        self.minmax_values_table.setSizePolicy(sizePolicy)
        self.minmax_values_table.setMinimumSize(QtCore.QSize(300, 250))
        self.minmax_values_table.setMaximumSize(QtCore.QSize(450, 230))
        self.minmax_values_table.setObjectName("minmax_values_table")
        self.minmax_values_table.setColumnCount(3)
        self.minmax_values_table.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.minmax_values_table.setHorizontalHeaderItem(2, item)
        self.minmax_values_table.horizontalHeader().setDefaultSectionSize(80)
        self.minmax_values_table.horizontalHeader().setMinimumSectionSize(30)
        self.minmax_values_table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_6.addWidget(self.minmax_values_table)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem3)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setMaximumSize(QtCore.QSize(380, 16777215))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.units_rbutton1 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton1.setChecked(True)
        self.units_rbutton1.setObjectName("units_rbutton1")
        self.verticalLayout_3.addWidget(self.units_rbutton1)
        self.units_rbutton2 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton2.setChecked(False)
        self.units_rbutton2.setObjectName("units_rbutton2")
        self.verticalLayout_3.addWidget(self.units_rbutton2)
        self.units_rbutton3 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton3.setObjectName("units_rbutton3")
        self.verticalLayout_3.addWidget(self.units_rbutton3)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.groupBox_8 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_8.setObjectName("groupBox_8")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.s1_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_8)
        self.s1_legend_checkbox.setObjectName("s1_legend_checkbox")
        self.horizontalLayout_11.addWidget(self.s1_legend_checkbox)
        self.s2_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_8)
        self.s2_legend_checkbox.setObjectName("s2_legend_checkbox")
        self.horizontalLayout_11.addWidget(self.s2_legend_checkbox)
        self.s3_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_8)
        self.s3_legend_checkbox.setObjectName("s3_legend_checkbox")
        self.horizontalLayout_11.addWidget(self.s3_legend_checkbox)
        self.s4_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_8)
        self.s4_legend_checkbox.setObjectName("s4_legend_checkbox")
        self.horizontalLayout_11.addWidget(self.s4_legend_checkbox)
        self.s5_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_8)
        self.s5_legend_checkbox.setObjectName("s5_legend_checkbox")
        self.horizontalLayout_11.addWidget(self.s5_legend_checkbox)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_11)
        self.verticalLayout_6.addWidget(self.groupBox_8)
        self.groupBox_7 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_7.setObjectName("groupBox_7")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.measure_interval_line_edit = QtWidgets.QSpinBox(self.groupBox_7)
        self.measure_interval_line_edit.setMinimum(1)
        self.measure_interval_line_edit.setMaximum(60)
        self.measure_interval_line_edit.setProperty("value", 1)
        self.measure_interval_line_edit.setObjectName("measure_interval_line_edit")
        self.horizontalLayout_6.addWidget(self.measure_interval_line_edit)
        self.label = QtWidgets.QLabel(self.groupBox_7)
        self.label.setObjectName("label")
        self.horizontalLayout_6.addWidget(self.label)
        self.verticalLayout_6.addWidget(self.groupBox_7)
        self.log_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.log_checkbox.setChecked(True)
        self.log_checkbox.setObjectName("log_checkbox")
        self.verticalLayout_6.addWidget(self.log_checkbox)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem5)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.copy_graph_button = QtWidgets.QPushButton(self.groupBox_4)
        self.copy_graph_button.setObjectName("copy_graph_button")
        self.horizontalLayout_8.addWidget(self.copy_graph_button)
        self.copy_data_button = QtWidgets.QPushButton(self.groupBox_4)
        self.copy_data_button.setObjectName("copy_data_button")
        self.horizontalLayout_8.addWidget(self.copy_data_button)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)
        self.horizontalLayout_13.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1307, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "СМЭП Клиент"))
        self.start_button.setText(_translate("MainWindow", "Начать новый сеанс"))
        self.open_button.setText(_translate("MainWindow", "Открыть сохраненный сеанс"))
        self.open_generator_button.setText(_translate("MainWindow", "Настройки генератора"))
        self.connection_settings_button.setText(_translate("MainWindow", "Настройки подключения"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Управление сеансом"))
        self.graph_start_button.setText(_translate("MainWindow", "Старт"))
        self.stop_button.setText(_translate("MainWindow", "Стоп"))
        self.groupBox.setTitle(_translate("MainWindow", "Размер скользящего окна"))
        self.label_2.setText(_translate("MainWindow", "час"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Параметры нормы и маркеров"))
        self.norma_checkbox.setText(_translate("MainWindow", "Норма"))
        self.norma_unit_label.setText(_translate("MainWindow", "В/м"))
        self.label_4.setText(_translate("MainWindow", "                "))
        self.marker_checkbox.setText(_translate("MainWindow", "Маркеры данных"))
        self.groupBox_9.setTitle(_translate("MainWindow", "Параметры интерфейса"))
        self.dark_theme_checkbox.setText(_translate("MainWindow", "Темная тема"))
        self.label_3.setText(_translate("MainWindow", "Язык"))
        self.groupBox_6.setTitle(_translate("MainWindow", "Заголовок графика"))
        item = self.minmax_values_table.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Датчик 1"))
        item = self.minmax_values_table.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "Датчик 2"))
        item = self.minmax_values_table.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "Датчик 3"))
        item = self.minmax_values_table.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "Датчик 4"))
        item = self.minmax_values_table.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "Датчик 5"))
        item = self.minmax_values_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Мин."))
        item = self.minmax_values_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Средн."))
        item = self.minmax_values_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Макс."))
        self.groupBox_2.setTitle(_translate("MainWindow", "Единицы измерения"))
        self.units_rbutton1.setText(_translate("MainWindow", "В/м"))
        self.units_rbutton2.setText(_translate("MainWindow", "дБмкВ/м"))
        self.units_rbutton3.setText(_translate("MainWindow", "Вт/м²"))
        self.groupBox_8.setTitle(_translate("MainWindow", "Отображение графиков"))
        self.s1_legend_checkbox.setText(_translate("MainWindow", "Д1"))
        self.s2_legend_checkbox.setText(_translate("MainWindow", "Д2"))
        self.s3_legend_checkbox.setText(_translate("MainWindow", "Д3"))
        self.s4_legend_checkbox.setText(_translate("MainWindow", "Д4"))
        self.s5_legend_checkbox.setText(_translate("MainWindow", "Д5"))
        self.groupBox_7.setTitle(_translate("MainWindow", "Период опроса датчиков"))
        self.label.setText(_translate("MainWindow", "сек"))
        self.log_checkbox.setText(_translate("MainWindow", "Писать в лог"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Копирование данных"))
        self.copy_graph_button.setText(_translate("MainWindow", "Копировать график"))
        self.copy_data_button.setText(_translate("MainWindow", "Копировать данные"))
try:
    from .CustomPlot import CustomPlot
except Exception as ex:
    from CustomPlot import CustomPlot