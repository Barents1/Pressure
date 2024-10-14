from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtWidgets
from gui.slide_pressure import SliderExample
from gui.gui_switch import SwitchButton
from utils.connection_utils import ConnectionUtils
from styles.style_pyqt5 import Style

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connection = ConnectionUtils()

    def initialize_ui(self):
        self.load_components()
        self.load_rute()
        self.styles_components()
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
        Style.button_success_style([
            self.main_window.btn_enable])
        Style.button_danger_style([
            self.main_window.btn_time_duration])
        """
        Style.button_success_style([
            self.btn_test_bomb1,
            self.btn_enviar_bomb1
            ])
        Style.button_warning_style([
            self.btn_test_bomb2,
            self.btn_enviar_bomb2
        ])
        Style.button_primary_style([
            self.btn_clean_bomb1,
            self.btn_clean_bomb2])
        Style.button_danger_style([
            self.btn_detener_bomb1,
            self.btn_detener_bomb2])
    """