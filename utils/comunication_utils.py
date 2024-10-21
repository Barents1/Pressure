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

        self.data_test = 729.011
    
    def value_pressure(self):
        #num = "R,729.011"
        num = "R,729.011 hPa a,-0.000 hPa/s,724.0399 hPa a"
        return num
    """
    def value_pressure(self):
        num = self.data_test + 1.011
        self.data_test = num
        return num
    """
    def get_pressure(self):
        if self.conn_bomb is None:
            QtWidgets.QMessageBox.critical(
                None, "Error", "La conexión no es válida"
            )
            return
        try:
            msg = "PRR\r\n"
            
            self.conn_bomb.write(msg.encode('ascii'))
            time.sleep(0.1)
            request = self.conn_bomb.readline(10).decode('ascii').strip()
            
            #request = self.value_pressure()
            #num_1 = request
            
            numbers = re.findall(r'-?\d+\.\d+', request)

            num_1 = float(numbers[0])
            #num_2 = float(numbers[1])
            #num_3 = float(numbers[2])

            print(f"Respuesta del dispositivo: {num_1}")
            return num_1
        
            #if len(numbers) >= 3:
                #num_1 = float(numbers[0])
                #num_2 = float(numbers[1])
                #num_3 = float(numbers[2])

                #print(f"Respuesta del dispositivo: {num_1}")
                #return num_1
            #else:
                #print("No se recibieron suficientes valores numéricos.")
                #return 0

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
    