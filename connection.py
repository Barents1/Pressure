from PyQt5 import QtWidgets, QtCore
from utils.connection_utils import ConnectionUtils
from utils.comunication_utils import ComunicationPressure
from utils.control_utils import ControlDevice
from utils.control_utils import PIDController
import time
import numpy as np
import os
import csv
from datetime import datetime

class PressureReaderThread(QtCore.QThread):
    pressure_value_reader_signal = QtCore.pyqtSignal(float)
    caj_value_reader_signal = QtCore.pyqtSignal(float)
    value_change_reader_pressure = QtCore.pyqtSignal(float)
    pressure_updated_signal = QtCore.pyqtSignal(float)
    set_point_error_signal = QtCore.pyqtSignal(float)

    def __init__(self, conn_bomb):
        super().__init__()
        self.conn_bomb = conn_bomb
        self.control = ControlDevice()
        self.is_running = True
        self.change_pressure = None
        self.state_set_point = False
        self.set_point_value = 700
        self.pid = PIDController(dt=2, min_output=0, max_output=5)
        self.current_pressure_value = None
        self.i = 0
        self.accumulator = 0

    def run(self):
        comunication = ComunicationPressure(self.conn_bomb)
        while self.is_running:
            value_pressure, error_dif = comunication.get_pressure()
            value_caj = comunication.get_patron_caj(value_pressure)

            # Actualiza el valor de la presión
            self.update_pressure_value(value_pressure)

            self.pressure_updated_signal.emit(value_pressure)
            self.pressure_value_reader_signal.emit(round(value_pressure, 6))
            self.caj_value_reader_signal.emit(round(value_caj, 6))

            #self.emit_pressure_difference(value_pressure)
            self.emit_pressure_difference(error_dif)
            self.process_set_point(value_pressure)

            time.sleep(1)

    def update_pressure_value(self, pressure_value):
        self.current_pressure_value = pressure_value

    def emit_pressure_difference(self, value_pressure):
        if self.change_pressure is None:
            self.change_pressure = value_pressure
        else:
            #difference = round(value_pressure - self.change_pressure, 6)
            #self.value_change_reader_pressure.emit(difference)
            #self.change_pressure = value_pressure
            self.value_change_reader_pressure.emit(value_pressure)

    def process_set_point(self, value_pressure):
        if self.state_set_point:
            self.set_point(self.set_point_value, value_pressure)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

    def change_state_set_point(self, state, set_point):
        self.state_set_point = state
        self.set_point_value = set_point

    def set_point(self, num_point, value_pressure):
        output, error = self.pid.calculate(num_point, value_pressure)
        print(f"Presión actual: {value_pressure}, Setpoint: {num_point}, Error: {error:.3f}")

        self.control.up_pressure(output)
        self.set_point_error_signal.emit(error)

        result, acum = self.stabilization(error)
        print(f"estabilizador = {result} y acumulador = {acum}")
        if result == 1:
            print("estabilizado")
            self.control.stop_all_tasks()
            self.change_state_set_point(False, num_point)

    def stabilization(self, error):
        # Usar una ventana de promediado para reducir fluctuaciones
        if self.i == 0:
            self.error_list = []  # Lista para acumular errores
        self.error_list.append(error)
        self.i += 1
        
        # Evaluar estabilidad después de 5 lecturas (ajustable)
        if len(self.error_list) >= 5:
            avg_error = sum(self.error_list) / len(self.error_list)
            if abs(avg_error) <= 0.5:  # Ajusta el umbral según tu necesidad
                self.accumulator += 1
            self.error_list.pop(0)  # Descartar la lectura más antigua
        
        if self.accumulator >= 4:  # Ajustar según los resultados
            result = 1
            self.i = 0
            self.accumulator = 0
            print("Estabilización alcanzada. Reiniciando variables.")
        else:
            result = 0
        
        return result, self.accumulator

class PressureDataThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(list)
    finished_data_signal = QtCore.pyqtSignal(float)
    time_remaining_signal = QtCore.pyqtSignal(float)

    def __init__(self, conn_bomb, num_chk, time_duration, output_dir, enable_time_check):
        super().__init__()
        self.conn_bomb = conn_bomb
        self.num_chk = num_chk
        self.is_running = True
        self.time_duration = time_duration * 60
        self._lock = QtCore.QMutex()
        self.output_dir = output_dir
        self.save_data = False
        self.enable_time_check = enable_time_check
        self.current_pressure_value = None
        self.paused = True
        self.paused_time = 0
        self.pause_start_time = None

    def update_pressure_value(self, pressure_value):
        self.current_pressure_value = pressure_value

    def get_csv_filename(self):
        now = datetime.now()
        filename = f"pressure_data_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        os.makedirs(self.output_dir, exist_ok=True)
        return os.path.join(self.output_dir, filename)

    def run(self):
        comunication = ComunicationPressure(self.conn_bomb)
        pa_a0, pa_a1 = str(comunication.pa_a0).replace('.', ','), str(comunication.pa_a1).replace('.', ',')

        # Esperar hasta que save_data sea True antes de iniciar el cronómetro
        while not self.save_data:
            if not self.is_running:
                return
            time.sleep(0.1)

        # Iniciar el cronómetro solo después de guardar datos
        time_initial = time.time()

        with open(self.get_csv_filename(), mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Fecha", "Hora", "Patron SAJ", "PA_A0", "PA_A1", "Patron CAJ"])

            while self.is_running:
                # Si está en pausa, solo espera sin afectar el cronómetro
                if self.paused:
                    time.sleep(0.1)
                    continue

                self.write_csv_data(writer, comunication, pa_a0, pa_a1)

                # Ajustar el tiempo de pausa si corresponde
                if self.pause_start_time:
                    self.paused_time += time.time() - self.pause_start_time
                    self.pause_start_time = None  # Resetear después de calcular

                elapsed_time = time.time() - time_initial - self.paused_time
                time_remaining = self.time_duration - elapsed_time

                self.time_remaining_signal.emit(round(time_remaining, 2))

                if self.enable_time_check and elapsed_time >= self.time_duration:
                    self.finished_data_signal.emit(round(elapsed_time, 4))
                    break

                time.sleep(1)

    def write_csv_data(self, writer, comunication, pa_a0, pa_a1):
        if int(datetime.now().strftime('%S')[-1]) == self.num_chk and self.save_data:
            date_data, time_data = comunication.get_date(), comunication.get_time()

            if self.current_pressure_value is None:
                print("Warning: self.current_pressure_value es None. Usando valor predeterminado 0.0.")
                self.current_pressure_value = 0.0
            patron_saj = f"{round(self.current_pressure_value, 6):.6f}".replace('.', ',')
            patron_caj = f"{round(comunication.get_patron_caj(self.current_pressure_value), 6):.6f}".replace('.', ',')
            list_data = [date_data, time_data, patron_saj, pa_a0, pa_a1, patron_caj]
            self.data_ready.emit(list_data)
            writer.writerow(list_data)

    def update_num_chk(self, new_num_chk):
        self._lock.lock()
        self.num_chk = new_num_chk
        self._lock.unlock()

    def pause_saving(self):
        self.save_data = False
        self.paused = True
        self.pause_start_time = time.time()

    def resume_saving(self):
        self.save_data = True
        self.paused = False
        if self.pause_start_time:
            self.paused_time += time.time() - self.pause_start_time
            self.pause_start_time = None

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

class ConnectionManager:
    def __init__(self, main_window, ui_manager):
        self.main_window = main_window
        self.ui_manager = ui_manager
        self.connection = ConnectionUtils()
        self.control = ControlDevice()
        self.conn_bomb = None
        self.data_thread = None
        self.reader_thread = None
        self.state_led_data = True
        self.state_led_motor = False
        self.state_led_sealed = False
        self.color_led_device()

    def load_port(self):
        self.connection.load_port(self.main_window.cbx_conn)

    def check_port(self):
        self.connection.check_port(self.main_window.cbx_conn)

    def connect_device(self):
        if not self.conn_bomb:
            self.conn_bomb = self.connection.connection_bomb_util(self.main_window.cbx_conn)
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Ya existe una conexion")

    def start_device(self):
        if self.conn_bomb:
            self.main_window.tbl_data.setRowCount(0)
            num_chk = int(self.main_window.inp_sync.text())
            
            time_duration = float(self.main_window.inp_time_duration.text().replace(',', '.'))

            self.ged_data_pressure(num_chk, time_duration)
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Realice la conexion")

    def color_led_data(self):
        self.main_window.led_data_save.setStyleSheet("background-color: green;" if self.state_led_data else "background-color: red;")

    def color_led_device(self):
        self.main_window.led_motor.setStyleSheet("background-color: green;" if self.state_led_motor else "background-color: red;")
        self.main_window.led_sealed.setStyleSheet("background-color: green;" if self.state_led_sealed else "background-color: red;")

    def ged_data_pressure(self, num_chk, time_duration):
        self.state_led_data = False
        self.color_led_data()
        _, output_dir = self.connection.read_or_create_file('file/data_rute.txt')

        enable_time_check = self.main_window.time_enable

        self.data_thread = PressureDataThread(self.conn_bomb, num_chk, time_duration, output_dir, enable_time_check)
        self.reader_thread = PressureReaderThread(self.conn_bomb)

        self.reader_thread.pressure_updated_signal.connect(self.data_thread.update_pressure_value)

        self.reader_thread.pressure_value_reader_signal.connect(self.set_value_pressure)
        self.reader_thread.pressure_value_reader_signal.connect(self.set_value_saj)

        self.reader_thread.value_change_reader_pressure.connect(self.set_change_pressure)
        self.reader_thread.caj_value_reader_signal.connect(self.set_value_caj)

        self.reader_thread.set_point_error_signal.connect(self.set_value_error)

        self.data_thread.data_ready.connect(self.set_table_item)
        self.data_thread.time_remaining_signal.connect(self.update_remaining_time)
        self.data_thread.finished_data_signal.connect(self.show_finished_message)

        self.data_thread.start()
        self.reader_thread.start()

    def change_num_chk(self):
        num_chk = int(self.main_window.inp_sync.text())
        if self.data_thread and self.data_thread.isRunning():
            self.state_led_data = True
            self.data_thread.resume_saving()
            self.data_thread.update_num_chk(num_chk)
        else:
            print("El hilo no está corriendo.")
            self.state_led_data = True
        self.color_led_data()

    def update_remaining_time(self, time_remaining):
        if time_remaining <= 0:
            self.main_window.inp_time_remaining.setText("0")
        else: 
            self.main_window.inp_time_remaining.setText(f"{time_remaining:.0f}")

    def active_set_point(self):
        num_point = int(self.main_window.inp_set_point.text())
        if self.reader_thread and self.reader_thread.isRunning():
            self.control.active_valvule()
            self.reader_thread.change_state_set_point(True, num_point)
            self.state_led_motor = True
            self.state_led_sealed = True
            self.color_led_device()
            time.sleep(0.1)
            state = self.control.check_port_digital()
            print(f"estado valvula = {state}")
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Inicie el programa")

    def stop_data_saving(self):
        if self.data_thread and self.data_thread.isRunning():
            self.data_thread.pause_saving()
            self.state_led_data = False
        else:
            print("El hilo no está corriendo.")
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

    def set_value_error(self, error_value):
        if self.conn_bomb:
            error_value = str(round(error_value, 4))
            self.main_window.inp_error_pressure.setText(error_value)

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

    def stop_device(self):
        num_point = int(self.main_window.inp_set_point.text())
        if self.reader_thread and self.reader_thread.isRunning():
            self.control.stop_all_tasks()
            state = self.control.check_port_digital()
            print(f"estado valvula = {state}")
            self.reader_thread.change_state_set_point(False, num_point)
            self.state_led_motor = False
            self.state_led_sealed = False
            self.color_led_device()
            print("detenido")
        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Inicie el programa")

    def show_finished_message(self, elapsed_time):
        self.close_bomb()
        QtWidgets.QMessageBox.information(
            None, "Advertencia", f"Ciclo concluido {elapsed_time} segundos"
        )

    def close_bomb(self):
        if self.data_thread:
            self.data_thread.stop()
        if self.reader_thread:
            self.reader_thread.stop()
        self.stop_device()
        self.conn_bomb = self.connection.close_connection()
        self.state_led_data = False
        self.color_led_data()
        self.main_window.inp_time_remaining.setText(f"{0:.0f}")
        QtWidgets.QMessageBox.information(None, "Advertencia", "Sistema detenido")