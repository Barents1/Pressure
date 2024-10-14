import serial
from datetime import datetime
import time
from PyQt5 import QtWidgets
import re

class ComunicationPressure:
    def __init__(self, conn_bomb):
        self.conn_bomb = conn_bomb
        self.patron_caj = None
        self.patron_saj = None
        self.pa_a0 = -0.179608
        self.pa_a1 = 1.0000782

    def value_pressure(self):
        num = "R,729.011 hPa a,-0.000 hPa/s,724.0399 hPa a"
        return num

    def get_pressure(self):
        if self.conn_bomb is None or not self.conn_bomb.is_open:
            QtWidgets.QMessageBox.critical(
                None, "Error", "La conexión no es válida"
            )
            return
        try:
            #msg = "*IDN?\r\n"
            msg = "PRR\r\n"
            #msg = "PR1?\r\n"
            
            #self.conn_bomb.write(msg.encode('ascii'))
            time.sleep(0.1)
            #respuesta = self.conn_bomb.readline().decode('ascii').strip()
            
            respuesta = self.value_pressure()
            numeros = re.findall(r'-?\d+\.\d+', respuesta)
            num_1 = float(numeros[0])
            num_2 = float(numeros[1])
            num_3 = float(numeros[2])
            print(f"Respuesta del dispositivo: {num_1}")
            return num_1
        except serial.SerialException as e:
            print(f"Error al enviar la instruccion: {e}")
            return 0

    def set_point(self, number):
        print(f"numero: {number}")
        msg = f"PSN {number} KPA\r\n"
        print(msg)
        self.conn_bomb.write(msg.encode('ascii'))

    def get_patron_caj(self, pressure_value):
        # Formula pressure_caj
        pressure_caj = (pressure_value * self.pa_a1) + self.pa_a0
        #print(f"Calculado pressure_caj: ({pressure_value} * {self.pa_a1}) + {self.pa_a0} = {pressure_caj}")
        return pressure_caj

    def get_date(self):
        current_date = datetime.now().strftime('%d/%m/%Y')
        return current_date

    def get_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        return current_time
    