from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtWidgets
from gui.slide_pressure import SliderExample
from gui.gui_switch import SwitchButton
from utils.connection_utils import ConnectionUtils

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connection = ConnectionUtils()

    def initialize_ui(self):
        self.load_components()
        self.load_rute()
        #self.set_value_slide()

    def load_components(self):
        self.main_window.tbl_data.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.slider_example = SliderExample()
        self.switch_frame = SwitchButton()

        layout = QVBoxLayout(self.main_window.f_comp_pressure)
        switch = QVBoxLayout(self.main_window.f_switch)

        layout.addWidget(self.slider_example)
        switch.addWidget(self.switch_frame)
        
        if not self.main_window.f_comp_pressure.layout():
            self.main_window.f_comp_pressure.setLayout(layout)
        if not self.main_window.f_switch.layout():
            self.main_window.f_switch.setLayout(layout)

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
        else:
            self.main_window.disable_button()
            self.main_window.btn_enable.setText("Habilitar")

    def toggle_button_time_state(self):
        if not self.main_window.inp_time_duration.isEnabled():
            self.main_window.enable_time()
            self.main_window.btn_time_duration.setText("Deshabilitar")
        else:
            self.main_window.disable_time()
            self.main_window.btn_time_duration.setText("Habilitar")
    