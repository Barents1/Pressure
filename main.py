"""
version: 1.00, fecha : 02/09/2024
class main
Copyright. INAMHI <www.inamhi.gob.ec>. Todos los derechos reservados.
"""
from PyQt5 import QtWidgets
from gui.gui_main import *
from ui_manager import UIManager
from connection import ConnectionManager

class MainMenu(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.ui_manager = UIManager(self)
        self.connection = ConnectionManager(self, self.ui_manager)
        self.connection.load_port()
        self.ui_manager.initialize_ui()
        self.initialize_actions()
        self.disable_button()
        self.time_enable = True

    def initialize_actions(self):
        self.cbx_conn.activated.connect(self.connection.check_port)
        self.btn_save_rute.clicked.connect(self.ui_manager.save_rute)
        self.btn_connect.clicked.connect(self.connection.connect_device)
        self.btn_start.clicked.connect(self.connection.start_device)
        self.btn_stop_conn.clicked.connect(self.connection.close_bomb)
        self.btn_start_conn.clicked.connect(self.connection.set_point)
        self.btn_enable.clicked.connect(self.ui_manager.toggle_button_state)
        self.btn_time_duration.clicked.connect(self.ui_manager.toggle_button_time_state) 
        self.btn_reset.clicked.connect(self.reset_value)    
        self.btn_finish_system.clicked.connect(self.connection.close_bomb)
        self.btn_save_ctrl_data.clicked.connect(self.connection.change_num_chk)
        self.btn_stop_ctrl_data.clicked.connect(self.connection.stop_data_saving)

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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())