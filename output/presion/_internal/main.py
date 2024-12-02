"""
version: 1.00, fecha : 15/11/2024
class main
Copyright. INAMHI <www.inamhi.gob.ec>. Todos los derechos reservados.
"""
from PyQt5 import QtWidgets
from gui.gui_main import *
from ui_manager import UIManager
from connection import ConnectionManager
from styles.style_pyqt5 import Style

class MainMenu(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.ui_manager = UIManager(self)
        self.connection = ConnectionManager(self, self.ui_manager)
        Style.set_window_size(self, 'main')
        self.connection.load_port()
        self.ui_manager.initialize_ui()
        self.initialize_actions()
        self.disable_button()
        self.styles_components()
        self.time_enable = False
        self.inp_time_remaining.setText(f"{0:.0f}")
        self.initial_button_state_pressure()
        self.initial_button_state_connection()

    def initialize_actions(self):
        """Inicializar las acciones de los botones"""
        self.cbx_conn.activated.connect(self.connection.check_port)
        self.btn_save_rute.clicked.connect(self.ui_manager.save_rute)
        self.btn_connect.clicked.connect(self.start_connection_button)
        self.btn_finish_system.clicked.connect(self.stop_connection_button)
        self.btn_enable.clicked.connect(self.ui_manager.toggle_button_state)
        self.btn_time_duration.clicked.connect(self.ui_manager.toggle_button_time_state) 
        self.btn_reset.clicked.connect(self.reset_value)    

        self.btn_save_ctrl_data.clicked.connect(self.connection.change_num_chk)
        self.btn_stop_ctrl_data.clicked.connect(self.connection.stop_data_saving)

        self.btn_start_conn.clicked.connect(self.start_button_change_pressure)
        self.btn_stop_conn.clicked.connect(self.stop_button_change_pressure)

    def initial_button_state_pressure(self):
        """Estado inicial de los botones para las valvulas"""
        self.btn_start_conn.setEnabled(True)
        self.btn_stop_conn.setEnabled(False)

    def start_button_change_pressure(self):
        if self.connection.active_set_point():
            self.btn_start_conn.setEnabled(False)
            self.btn_stop_conn.setEnabled(True)
            Style.button_danger_style([self.btn_stop_conn])
            Style.button_disabled_style([self.btn_start_conn])

    def stop_button_change_pressure(self):
        if self.connection.stop_device():
            self.btn_start_conn.setEnabled(True)
            self.btn_stop_conn.setEnabled(False)
            Style.button_success_style([self.btn_start_conn])
            Style.button_disabled_style([self.btn_stop_conn])

    def initial_button_state_connection(self):
        """Estado inicial de los botones conexion"""
        self.btn_connect.setEnabled(True)
        self.btn_finish_system.setEnabled(False)

    def start_connection_button(self):
        if self.connection.connect_device():
            self.btn_connect.setEnabled(False)
            self.btn_finish_system.setEnabled(True)
            Style.button_danger_style([self.btn_finish_system])
            Style.button_disabled_style([self.btn_connect])

    def stop_connection_button(self):   
        self.connection.close_bomb()
        self.btn_connect.setEnabled(True)
        self.btn_finish_system.setEnabled(False)
        self.btn_start_conn.setEnabled(True)
        self.btn_stop_conn.setEnabled(False)
        Style.button_success_style([self.btn_start_conn])
        Style.button_primary_style([self.btn_connect])
        Style.button_disabled_style([self.btn_finish_system, self.btn_stop_conn])

    def automatic_change(self):
        self.btn_start_conn.setEnabled(True)
        self.btn_stop_conn.setEnabled(False)
        Style.button_success_style([self.btn_start_conn])
        Style.button_disabled_style([self.btn_stop_conn])

    def enable_button(self):
        self.inp_a0.setEnabled(True)
        self.inp_a1.setEnabled(True)

    def disable_button(self):
        self.inp_a0.setEnabled(False)
        self.inp_a1.setEnabled(False)

    def enable_time(self):
        self.inp_time_duration.setEnabled(True)
        self.time_enable = True

    def disable_time(self):
        self.inp_time_duration.setEnabled(False)
        self.time_enable = False

    def reset_value(self):
        pa_a0, pa_a1 = self.connection.get_value_reset()
        self.inp_a0.setValue(pa_a0)
        self.inp_a1.setValue(pa_a1)

    def styles_components(self):
        Style.window_bgd_styles([
            self.centralwidget])
        Style.button_success_style([
            self.btn_enable,
            self.btn_save_ctrl_data,
            self.btn_start_conn
            ])
        Style.button_disabled_style([
            self.btn_stop_conn,
            self.btn_finish_system
            ])
        Style.button_danger_style([
            self.btn_stop_ctrl_data
            ])
        Style.button_warning_style([
            self.btn_reset,
            self.btn_save_rute
        ])
        Style.button_primary_style([
            self.btn_connect])
        Style.frame_bgd_white_styles([
            self.cbx_conn,
            self.inp_rute,
            self.inp_current_pressure,
            self.inp_error_pressure,
            self.inp_set_point,
            self.inp_pressure_saj,
            self.inp_pressure_caj,
            self.inp_time_duration,
            self.inp_change_pressure,
            self.inp_sync,
            self.inp_a1,
            self.inp_a0,
            self.inp_time_remaining,
            self.tbl_data,
            self.inp_set_point_establish
            ])
        Style.combo_size_device_styles([
            self.cbx_conn
            ])
        Style.inp_size_styles([
            self.inp_current_pressure,
            self.inp_error_pressure,
            self.inp_set_point,
            self.inp_set_point_establish,
            self.inp_pressure_saj,
            self.inp_pressure_caj,
            self.inp_time_duration,
            self.inp_change_pressure,
            self.inp_sync,
            self.inp_a1,
            self.inp_a0,
            self.inp_time_remaining
            ])
        Style.label_inp_styles([
            self.cbx_conn,
            self.inp_rute])
        Style.label_title_instruction_styles([
            self.lbl_conn,
            self.f_lbl_title_2,
            self.lbl_indicator_1,
            self.lbl_ctrl_1,
            self.lbl_data,
            self.lbl_value_a1,
            self.lbl_ctrl_2,
            self.lbl_ctrl_5,
            self.lbl_indicator_2,
            self.lbl_pressure_2
        ])
        Style.label_sub_instructiol_styles([
            self.lbl_rute,
            self.lbl_pressure,
            self.lbl_control_1,
            self.lbl_current_pressure,
            self.lbl_control_2,
            self.lbl_setpoint_4,
            self.lbl_setpoint_5,
            self.lbl_ctrl_3,
            self.lbl_ctrl_4,
            self.lbl_a1_2,
            self.lbl_a0,
            self.lbl_s_1,
            self.lbl_sensor_1,
            self.lbl_time_remaining,
            self.lbl_pressure_saj,
            self.lbl_pressure_caj,
            self.lbl_motor,
            self.lbl_sealed,
            self.lbl_time_duration,
            self.lbl_change_pressure
        ])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())