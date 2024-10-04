from PyQt5 import QtWidgets, QtCore
from utils.connection_utils import ConnectionUtils
from utils.comunication_utils_1 import ComunicationPressure
from utils.comunication_utils import ComunicationSerial
import time
import os
import csv
from datetime import datetime

class PressureDataThread(QtCore.QThread):

    data_ready = QtCore.pyqtSignal(list)
    finished_signal = QtCore.pyqtSignal(float)
    pressure_value_signal = QtCore.pyqtSignal(float)
    caj_value_signal = QtCore.pyqtSignal(float)
    value_change_pressure = QtCore.pyqtSignal(float)

    def __init__(self, conn_bomb, num_chk, time_duration, output_dir, enable_time_check):
        super().__init__()
        self.conn_bomb = conn_bomb
        self.num_chk = num_chk
        self.is_running = True
        self.time_duration = time_duration * 60
        self._lock = QtCore.QMutex() 
        self.output_dir = output_dir
        self.save_data = True
        self.change_pressure = 0
        self.enable_time_check = enable_time_check

    def get_csv_filename(self):
        now = datetime.now()

        day_week = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        day_current = day_week[now.weekday()]

        filename = now.strftime(f"{day_current}_%d-%m-%Y-%H_%M_%S.csv")
        return os.path.join(self.output_dir, filename)

    def run(self):
        time_initial = time.time()
        comunication = ComunicationPressure(self.conn_bomb)
        pa_a0 = comunication.pa_a0
        pa_a1 = comunication.pa_a1

        csv_filename = self.get_csv_filename()
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Hora", "Patron SAJ", "PA_A0", "PA_A1", "Patron CAJ"])

            while self.is_running:
                current_second = datetime.now().strftime('%S')
                last_num = int(current_second[-1])

                value_pressure = comunication.get_pressure()
                value_caj = comunication.get_patron_caj(value_pressure)
                self.pressure_value_signal.emit(value_pressure)
                self.caj_value_signal.emit(value_caj)

                self._lock.lock()
                current_num_chk = self.num_chk
                current_enable_time_check = self.enable_time_check
                self._lock.unlock()

                if last_num == current_num_chk:
                    patron_saj = comunication.get_pressure()
                    date_data = comunication.get_date()
                    time_data = comunication.get_time()
                    patron_caj = comunication.get_patron_caj(patron_saj)
                    list_data = [date_data, time_data, patron_saj, pa_a0, pa_a1, patron_caj]

                    self.data_ready.emit(list_data)

                    if self.save_data:
                        writer.writerow(list_data)
                    
                time.sleep(1)

                if self.change_pressure <= value_pressure:
                    self.change_pressure = value_pressure - self.change_pressure
                    self.value_change_pressure.emit(self.change_pressure)
                else: 
                    self.change_pressure = self.change_pressure - value_pressure
                    self.value_change_pressure.emit(self.change_pressure)

                elapsed_time = time.time() - time_initial

                if current_enable_time_check:
                    if elapsed_time >= self.time_duration:
                        self.finished_signal.emit(elapsed_time)
                        break

    def update_num_chk(self, new_num_chk):
        self._lock.lock()
        self.num_chk = new_num_chk
        self._lock.unlock()

    def pause_saving(self):
        self.save_data = False

    def resume_saving(self):
        self.save_data = True

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

class ConnectionManager:
    def __init__(self, main_window, ui_manager):
        self.main_window = main_window
        self.ui_manager = ui_manager
        self.connection = ConnectionUtils()
        self.conn_bomb = None
        self.thread = None
        self.state_led_data = True

    def load_port(self):
        self.connection.load_port(self.main_window.cbx_conn)

    def check_port(self):
        self.connection.check_port(self.main_window.cbx_conn)

    def connect_bomb(self):
        if not self.conn_bomb:
            self.conn_bomb = self.connection.connection_bomb_util(self.main_window.cbx_conn)
            comunication = ComunicationPressure(self.conn_bomb)
            value_pressure = comunication.get_pressure()
            #self.set_value_pressure(value_pressure)

            num_chk = int(self.main_window.inp_sync.text())
            
            time_duration = float(self.main_window.inp_time_duration.text().replace(',', '.'))

            self.ged_data_pressure(num_chk, time_duration)
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Ya existe una conexion")

    def color_led_data(self):
        self.main_window.led_data_save.setStyleSheet("background-color: green;" if self.state_led_data else "background-color: red;")

    def ged_data_pressure(self, num_chk, time_duration):
        self.color_led_data()
        _, output_dir = self.connection.read_or_create_file('file/data_rute.txt')

        enable_time_check = self.main_window.time_enable

        self.thread = PressureDataThread(self.conn_bomb, num_chk, time_duration, output_dir, enable_time_check)

        self.thread.pressure_value_signal.connect(self.set_value_pressure)
        self.thread.pressure_value_signal.connect(self.set_value_saj)
        self.thread.value_change_pressure.connect(self.set_change_pressure)
        self.thread.caj_value_signal.connect(self.set_value_caj)
        self.thread.data_ready.connect(self.set_table_item)
        self.thread.finished_signal.connect(self.show_finished_message)

        self.thread.start()

    def change_num_chk(self):
        num_chk = int(self.main_window.inp_sync.text())
        if self.thread and self.thread.isRunning():
            self.state_led_data = True
            self.thread.resume_saving()
            self.thread.update_num_chk(num_chk)
        else:
            print("El hilo no está corriendo.")
        self.color_led_data()

    def stop_data_saving(self):
        self.thread.pause_saving()
        self.state_led_data = False
        self.color_led_data()

    def set_table_item(self, data):
        row_number = self.main_window.tbl_data.rowCount()
        self.main_window.tbl_data.insertRow(row_number)
        for column_number, item in enumerate(data):
            self.main_window.tbl_data.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(item)))

    def get_value_reset(self):
        comunication = ComunicationPressure(self.conn_bomb)
        value_origin = [comunication.pa_a0, comunication.pa_a1]
        return value_origin

    def set_value_pressure(self, value_pressure):
        if self.conn_bomb:
            self.main_window.inp_current_pressure.setValue(value_pressure)
            self.ui_manager.set_value_slide(value_pressure)

    def set_value_saj(self, num_pressure):
        value_pressure = str(num_pressure)
        if self.conn_bomb:
            self.main_window.inp_pressure_saj.setText(value_pressure)

    def set_value_caj(self, num_caj):
        value_caj = str(num_caj)
        if self.conn_bomb:
            self.main_window.inp_pressure_caj.setText(value_caj)

    def set_change_pressure(self, num_change):
        value_change = str(num_change)
        if self.conn_bomb:
            self.main_window.inp_change_pressure.setText(value_change)

    def set_point(self):
        num_point = self.main_window.inp_set_point.text()
        if self.conn_bomb:
            comunication = ComunicationSerial(self.conn_bomb)
            comunication.set_point_example(num_point)
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Realice la conexion")

    def show_finished_message(self, elapsed_time):
        self.close_bomb()
        QtWidgets.QMessageBox.information(
            None, "Advertencia", f"Ciclo concluido {elapsed_time} segundos"
        )

    def close_bomb(self):
        if self.thread:
            self.thread.stop()
        self.stop_data_saving()
        self.conn_bomb = self.connection.close_connection()
        QtWidgets.QMessageBox.information(
            None, "Advertencia", f"Sistema detenido"
        )