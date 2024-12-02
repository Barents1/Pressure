from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtCore, QtWidgets, QtGui
from gui.slide_pressure import SliderExample
from gui.gui_switch import SwitchButton
from utils.connection_utils import ConnectionUtils
from styles.style_pyqt5 import Style
import os

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connection = ConnectionUtils()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    def initialize_ui(self):
        self.load_components()
        self.load_rute()
        self.styles_components()
        self.toggle_button_time_state()
        self.load_icon()

    def load_components(self):
        self.main_window.tbl_data.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.slider_example = SliderExample()
        self.switch_frame = SwitchButton()

        layout = QVBoxLayout(self.main_window.f_comp_pressure)
        # switch = QVBoxLayout(self.main_window.f_switch)

        layout.addWidget(self.slider_example)
        # switch.addWidget(self.switch_frame)
        
        if not self.main_window.f_comp_pressure.layout():
            self.main_window.f_comp_pressure.setLayout(layout)
        # if not self.main_window.f_switch.layout():
        #     self.main_window.f_switch.setLayout(layout)

    def load_icon(self):
        ruta_logo = os.path.normpath(os.path.join(self.current_dir, "img/inamhi-logo.png"))
        pix_logo = QtGui.QPixmap(ruta_logo)
        self.main_window.lbl_img.setPixmap(pix_logo.scaled(self.main_window.lbl_img.size(), QtCore.Qt.KeepAspectRatio))
        self.main_window.lbl_img.repaint()

    def save_rute(self):
        folder_path = self.connection.open_folder_dialog(self.main_window)
        if folder_path:
            self.connection.save_rute_to_file('file/data_rute.txt', folder_path)
            self.main_window.inp_rute.setText(folder_path)

    def load_rute(self):
        _, rute_content = self.connection.read_or_create_file('file/data_rute.txt')
        if rute_content:
            self.main_window.inp_rute.setText(rute_content)

    def set_value_slide(self, value):
        if self.slider_example:
            self.main_window.inp_current_pressure.setValue(value)
            value = round(value)
            self.slider_example.slider.setValue(value)

    def toggle_button_state(self):
        if not self.main_window.inp_a0.isEnabled():
            self.main_window.enable_button()
            self.main_window.btn_enable.setText("Deshabilitar")
            Style.button_danger_style([self.main_window.btn_enable])
        else:
            self.main_window.disable_button()
            self.main_window.btn_enable.setText("Habilitar")
            Style.button_success_style([self.main_window.btn_enable])

    def toggle_button_time_state(self):
        if not self.main_window.inp_time_duration.isEnabled():
            self.main_window.enable_time()
            self.main_window.btn_time_duration.setText("Deshabilitar")
            Style.button_danger_style([self.main_window.btn_time_duration])
        else:
            self.main_window.disable_time()
            self.main_window.btn_time_duration.setText("Habilitar")
            Style.button_success_style([self.main_window.btn_time_duration])

    def styles_components(self):
        Style.img_size_logo_styles([
            self.main_window.lbl_img
        ])
        Style.button_success_style([
            self.main_window.btn_enable,
            self.main_window.btn_save_ctrl_data,
            self.main_window.btn_start_conn,
            self.main_window.btn_time_duration
            ])
        Style.button_danger_style([
            self.main_window.btn_stop_ctrl_data,
            self.main_window.btn_finish_system,
            self.main_window.btn_stop_conn
            ])