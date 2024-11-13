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
        self.data_test = 925.011
        self.direction = 1

    """
    def value_pressure(self):
        #num = "R,729.011"
        num = "R,729.011 hPa a,-0.000 hPa/s,724.0399 hPa a"
        return num
    """
    def value_pressure(self):
        if self.direction == 1 and self.data_test >= 950:
            self.direction = -1
        elif self.direction == -1 and self.data_test <= 930:
            self.direction = 1

        self.data_test += self.direction * 1.011
        return self.data_test, 0.001
    
    def get_pressure(self):
        if self.conn_bomb is None:
            QtWidgets.QMessageBox.critical(
                None, "Error", "La conexión no es válida"
            )
            return
        try:
            msg = "PRR\r\n"
            self.conn_bomb.write(msg.encode('ascii'))
            #time.sleep(0.1)
            time.sleep(0.5)
            
            # request, error = self.value_pressure()
            # num_1 = request
            # num_2 = error

            request = ""
            while True:
                chunk = self.conn_bomb.readline(50).decode('ascii')
                request += chunk
                if '\n' in chunk:
                    break
            
            request = request.strip()
            numbers = re.findall(r'-?\d+\.\d+', request)

            if len(numbers) >= 2:
                num_1 = float(numbers[0])
                num_2 = float(numbers[1])
                print(f"Presión obtenida: {num_1} hPa, Cambio de presión: {num_2} hPa/s")
                return num_1, num_2
            else:
                print("No se encontraron suficientes valores numéricos.")
                return 0, 0
            
            # print(f"Respuesta del dispositivo: {num_1}, {num_2}")
            # return num_1, num_2

        except serial.SerialException as e:
            print(f"Error al enviar la instruccion: {e}")
            return 0, 0

    def get_patron_caj(self, pressure_value):
        if pressure_value is None:
            pressure_value = 0  # o cualquier valor predeterminado
        return (pressure_value * self.pa_a1) + self.pa_a0

    def get_date(self):
        current_date = datetime.now().strftime('%d/%m/%Y')
        return current_date

    def get_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        return current_time
    