from PyQt5 import QtWidgets, QtCore
from utils.connection_utils import ConnectionUtils
from utils.comunication_utils import ComunicationPressure
from utils.connection_daq_utils import AnalogInput
from utils.connection_daq_utils import AnalogOutput
from utils.connection_daq_utils import DigitalOutput
import time
import numpy as np
import os
import csv
from datetime import datetime

class PressureReaderThread(QtCore.QThread):
    pressure_value_reader_signal = QtCore.pyqtSignal(float)
    caj_value_reader_signal = QtCore.pyqtSignal(float)
    value_change_reader_pressure = QtCore.pyqtSignal(float)

    def __init__(self, conn_bomb):
        super().__init__()
        self.conn_bomb = conn_bomb
        self.is_running = True
        self.change_pressure = None

    def run(self):
        comunication = ComunicationPressure(self.conn_bomb)
        while self.is_running:
            
            value_pressure = comunication.get_pressure()
            value_caj = comunication.get_patron_caj(value_pressure)

            self.pressure_value_reader_signal.emit(round(value_pressure, 6))
            self.caj_value_reader_signal.emit(round(value_caj, 6))

            if self.change_pressure is None:
                self.change_pressure = value_pressure
            else:
                difference = value_pressure - self.change_pressure
                difference = round(difference, 6)
                self.value_change_reader_pressure.emit(difference)
                self.change_pressure = value_pressure

            time.sleep(2)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

class PressureDataThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(list)
    finished_data_signal = QtCore.pyqtSignal(float)

    def __init__(self, conn_bomb, num_chk, time_duration, output_dir, enable_time_check):
        super().__init__()
        self.conn_bomb = conn_bomb
        self.num_chk = num_chk
        self.is_running = True
        self.time_duration = time_duration * 60
        self._lock = QtCore.QMutex() 
        self.output_dir = output_dir
        self.save_data = True
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
        pa_a0 = str(comunication.pa_a0).replace('.', ',')
        pa_a1 = str(comunication.pa_a1).replace('.', ',')

        csv_filename = self.get_csv_filename()
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Fecha", "Hora", "Patron SAJ", "PA_A0", "PA_A1", "Patron CAJ"])

            while self.is_running:
                current_second = datetime.now().strftime('%S')
                last_num = int(current_second[-1])

                self._lock.lock()
                current_num_chk = self.num_chk
                current_enable_time_check = self.enable_time_check
                self._lock.unlock()

                if self.save_data:
                    if last_num == current_num_chk:

                        time_data = comunication.get_time()
                        patron_saj = comunication.get_pressure()
                        date_data = comunication.get_date()
                        patron_caj = comunication.get_patron_caj(patron_saj)

                        patron_saj = f"{round(patron_saj, 6):.6f}".replace('.', ',')
                        patron_caj = f"{round(patron_caj, 6):.6f}".replace('.', ',')

                        list_data = [date_data, time_data, patron_saj, pa_a0, pa_a1, patron_caj]

                        self.data_ready.emit(list_data)
                        writer.writerow(list_data)

                time.sleep(1)

                elapsed_time = time.time() - time_initial

                if current_enable_time_check:
                    if elapsed_time >= self.time_duration:
                        elapsed_time = round(elapsed_time, 4)
                        self.finished_data_signal.emit(elapsed_time)
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
        self.data_thread = None
        self.reader_thread = None
        self.state_led_data = True

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

    def ged_data_pressure(self, num_chk, time_duration):
        self.color_led_data()
        _, output_dir = self.connection.read_or_create_file('file/data_rute.txt')

        enable_time_check = self.main_window.time_enable

        #self.thread = PressureDataThread(self.conn_bomb, num_chk, time_duration, output_dir, enable_time_check)

        self.data_thread = PressureDataThread(self.conn_bomb, num_chk, time_duration, output_dir, enable_time_check)
        self.reader_thread = PressureReaderThread(ComunicationPressure(self.conn_bomb))

        self.reader_thread.pressure_value_reader_signal.connect(self.set_value_pressure)
        self.reader_thread.pressure_value_reader_signal.connect(self.set_value_saj)

        self.reader_thread.value_change_reader_pressure.connect(self.set_change_pressure)
        self.reader_thread.caj_value_reader_signal.connect(self.set_value_caj)
        self.data_thread.data_ready.connect(self.set_table_item)
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
        self.color_led_data()

    def stop_data_saving(self):
        self.data_thread.pause_saving()
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
            comunication = ComunicationPressure(self.conn_bomb)
            comunication.get_device_out()

            # channelIN = "Dev1/ai0"
            # analog_input = AnalogInput(channelIN)
            #analog_input.start()
            
            # Leer datos
            # data = analog_input.read()
            # print(f"Datos leídos: {data}")
            
            # Detener la tarea
            # analog_input.stop()
            # analog_input.clear()

            # escribir datos analogicos
            channelOUT = "Dev1/ao0"
            analog_output = AnalogOutput(channelOUT)
            # data = np.array([1.1])
            # analog_output.write(data)

            # analog_output.stop()
            # analog_output.clear()
            
            #escribir datos digitales 
            
            # digital_output = DigitalOutput("Dev1/port0/line0:1") 
            # digital_output.write([1, 0])

        else:
            QtWidgets.QMessageBox.information(None, "Informacion", "Realice la conexion")

    def control_solenoid(self, state):
        # Aquí 'state' será 1 para activar y 0 para desactivar
        if self.conn_bomb:
            # Configurar el canal digital que controlará el relé
            digital_output = DigitalOutput("Dev1/port0/line0")  # Ajusta este canal a tu configuración de hardware

            # Enviar el estado al relé: 1 = activado, 0 = desactivado
            digital_output.write([state])

            # Detener la tarea y limpiar
            digital_output.stop()
            digital_output.clear()

            QtWidgets.QMessageBox.information(None, "Información", "La válvula solenoide ha sido " + ("activada" if state == 1 else "desactivada"))

        else:
            QtWidgets.QMessageBox.information(None, "Información", "Realice la conexión")

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
        self.conn_bomb = self.connection.close_connection()
        QtWidgets.QMessageBox.information(None, "Advertencia", "Sistema detenido")