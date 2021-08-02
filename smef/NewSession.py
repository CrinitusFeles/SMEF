import json
from PyQt5.QtWidgets import QWidget, QMessageBox
from .new_session_window import *
from types import SimpleNamespace
from .app_logger import *
import time

logger = get_logger(__name__)


class NewSession(QWidget, Ui_new_session_window):
    def __init__(self, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Новый сеанс')
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.path_tool_button.pressed.connect(self.open_file_system)
        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)
        self.generate_name_button.pressed.connect(self.generate_name)

        self.path_line_edit.setText(kwargs.get('path', ''))
        self.filename_line_edit.setText(kwargs.get('name', ''))

        self.s1_checkbox.setChecked(kwargs.get('s1', False))
        self.s2_checkbox.setChecked(kwargs.get('s2', False))
        self.s3_checkbox.setChecked(kwargs.get('s3', False))
        self.s4_checkbox.setChecked(kwargs.get('s4', False))
        self.s5_checkbox.setChecked(kwargs.get('s5', False))

        self.generate_name()

        self.status = False

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def accept_clicked(self):
        with open('config.json') as f:
            config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
        config.last_path = self.path_line_edit.text()
        config.last_name = self.filename_line_edit.text()
        config.connected_sensors = [self.s1_checkbox.isChecked(), self.s2_checkbox.isChecked(),
                                    self.s3_checkbox.isChecked(), self.s4_checkbox.isChecked(),
                                    self.s5_checkbox.isChecked()]
        config.comment = self.session_comment_editor.toPlainText()

        if self.path_line_edit.text() != '':
            if not os.path.isdir(self.path_line_edit.text()):
                logger.info('Create new output folder' + self.path_line_edit.text())
                os.makedirs(self.path_line_edit.text(), exist_ok=True)
            else:
                logger.info('Output folder exists')
        else:
            QMessageBox.warning(self, 'Warning', "Укажите путь к папке с сессией.",
                                QMessageBox.Ok, QMessageBox.Ok)
            logger.warning('Session path is empty. Show warning dialog')

        if self.filename_line_edit.text() != '':
            if self.s1_checkbox.isChecked() or self.s2_checkbox.isChecked() or self.s3_checkbox.isChecked() or self.s4_checkbox.isChecked() or self.s5_checkbox.isChecked():
                self.status = True
                with open('config.json', 'w') as f:
                    f.write(json.dumps(config, default=lambda o: o.__dict__, sort_keys=True, indent=4))
                with open(self.path_line_edit.text() + '\\' + self.filename_line_edit.text() + '.csv', 'w') as log:
                    log_sting = 'Timestamp;Time;'
                    if self.s1_checkbox.isChecked():
                        log_sting += 'Sensor1;'
                    if self.s2_checkbox.isChecked():
                        log_sting += 'Sensor2;'
                    if self.s3_checkbox.isChecked():
                        log_sting += 'Sensor3;'
                    if self.s4_checkbox.isChecked():
                        log_sting += 'Sensor4;'
                    if self.s5_checkbox.isChecked():
                        log_sting += 'Sensor5;'
                    if self.session_comment_editor.toPlainText() != '':
                        log.write(log_sting + self.session_comment_editor.toPlainText().replace('\n', ' ').replace(';', ',') + '\n')
                    else:
                        log.write(log_sting[:-1] + '\n')
                    # log.write(log_sting + '\n')
                self.close()
            else:
                QMessageBox.warning(self, 'Warning', "Хотя бы один из датчиков должен быть подключен.",
                                    QMessageBox.Ok, QMessageBox.Ok)
                logger.warning('Sensors checkboxes are empty. Show warning dialog')
        else:
            QMessageBox.warning(self, 'Warning', "Укажите название сеанса.", QMessageBox.Ok, QMessageBox.Ok)
            logger.warning('Session name is empty. Show warning dialog')

    def cancel_clicked(self):
        logger.info('Cancel button clicked')
        self.close()

    def open_file_system(self):
        logger.info('Open explorer window clicked')
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        file_dialog.setDirectory(self.path_line_edit.text())
        file_dialog.open()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            logger.info('Accept button clicked')
            file_full_path = str(file_dialog.selectedFiles()[0])
            self.path_line_edit.setText(file_full_path)
        else:
            logger.info('Close file dialog')
            # self.plot_from_file(file_full_path)

    def generate_name(self):
        self.filename_line_edit.setText(time.strftime("%Y-%m-%d_%H.%M", time.localtime()))
