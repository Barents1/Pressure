import serial
import time
import re
import numpy as np
from datetime import datetime
from PyQt5 import QtWidgets

class ComunicationSerial:
    def __init__(self, conn_bomb):
        self.conn_bomb = conn_bomb
        self.byte_count = 50
        self.event_time = 100
        self.a0 = -0.179608
        self.a1 = 1.0000782
        self.pressure_caj = None

        # Simulación de los shift registers
        self.shift_register_array1 = []
        self.shift_register_array2 = []
        self.shift_register_array3 = []
        self.shift_register_combined = []

    def example_test_1(self):
        print(self.conn_bomb)
        if self.conn_bomb is None or not self.conn_bomb.is_open:
            QtWidgets.QMessageBox.critical(
                None, "Error", "La conexión no es válida"
            )
            return
        try:
            #msg = "*IDN?\r\n"
            #msg = "PRR\r\n"
            msg = "PR1?\r\n"
            self.conn_bomb.write(msg.encode('ascii'))
            time.sleep(0.1)
            respuesta = self.conn_bomb.readline().decode('ascii').strip()
            print(f"Respuesta del dispositivo: {respuesta}")
        except serial.SerialException as e:
            print(f"Error al enviar la instruccion: {e}")

    def set_point_example(self, number):
        print(f"numero: {number}")
        msg = f"PSN {number} KPA\r\n"
        print(msg)
        self.conn_bomb.write(msg.encode('ascii'))

    def set_command(self):
        if self.conn_bomb is None or not self.conn_bomb.is_open:
            QtWidgets.QMessageBox.critical(
                None, "Error", "La conexión no es válida"
            )
            return

        comand = "PRR\r\n"  # Envío de comando con CR y LF
        self.conn_bomb.write(comand.encode())
        time.sleep(1)

        response = self.result_comand()
        print(f"response: {response}")
        #response = 565,756.63,12,11 prueba
        #return primera prueba
        if response:
            value1, pressure_caj, value2, value3 = response

            # Procesar y almacenar en arrays (simulando los shift registers)
            #return segunda prueba
            self.process_shift_register(value1, pressure_caj, value2, value3)
            
            QtWidgets.QMessageBox.information(
                None, "Respuesta", f"Valores recibidos:\n"
                                    f"Valor 1: {value1}\n"
                                    f"Presión Caj: {pressure_caj}\n"
                                    f"Valor 2: {value2}\n"
                                    f"Valor 3: {value3}"
            )
            return response
        else:
            QtWidgets.QMessageBox.critical(
                None, "Error", "No se recibió ninguna respuesta válida"
            )
            return None, None, None, None

    def result_comand(self):
        if self.conn_bomb is None:
            print("Error: No hay una conexión serial válida.")
            return None

        initial_time = time.time()
        while time.time() - initial_time < self.event_time / 1000.0:
            if self.conn_bomb.in_waiting > 0:
                break
            time.sleep(0.01)

        if self.conn_bomb.in_waiting == 0:
            print(f"No se recibieron datos en {self.event_time} ms.")
            return None

        try:
            data = self.conn_bomb.read(self.byte_count).decode().strip()
            print(f"Datos recibidos de respuesta: {data}")

            patron = r"(.*)(\r\n)$"
            search = re.search(patron, data)

            if search:
                content = search.group(1)
                print(f"Contenido antes de CR+LF: {content}")

                # Procesar los datos
                return self.process_data(content)

            else:
                print("El patrón CR+LF no fue encontrado en los datos.")
                return None

        except serial.SerialException as e:
            print(f"Error al leer del puerto serial: {e}")
            return None

    def process_data(self, data):
        part = data.split(",")

        if len(part) > 3:
            value1_str = part[1]  # Presión actual (index 1)
            value2_str = part[2]  # Otro valor (index 2)
            value3_str = part[3]  # Otro valor (index 3)

            value1, pressure_caj = self.process_value1(value1_str)
            value2 = self.process_value2(value2_str)
            value3 = self.process_value3(value3_str)

            if value1 is not None and pressure_caj is not None and value2 is not None and value3 is not None:
                return value1, pressure_caj, value2, value3
            else:
                print("Uno o más valores no pudieron procesarse correctamente.")
                return None
        else:
            print("Los datos recibidos no tienen suficientes elementos.")
            return None

    def process_value1(self, value1_str):
        print(f"Valor en process_value1: {value1_str}")
        value1 = self.scan_value(value1_str)

        if value1 is not None:
            pressure_caj = self.calculate_pressure(value1)
            print(f"Resultado de pressure_caj: {pressure_caj}")
            self.pressure_caj = pressure_caj
            return value1, pressure_caj
        else:
            return None, None

    def calculate_pressure(self, pressure_value):
        """Aplica la fórmula de LabVIEW para calcular pressure_caj"""
        # Formula: pressure_caj = (value * a0) + a1
        pressure_caj = (pressure_value * self.a0) + self.a1
        print(f"Calculado pressure_caj: (value * {self.a0}) + {self.a1} = {pressure_caj}")
        return pressure_caj

    def process_value2(self, value2_str):
        print(f"Valor en process_value2: {value2_str}")
        value2 = self.scan_value(value2_str)
        if value2 is not None:
            print(f"Valor2 procesado: {value2}")
            return value2
        else:
            return None

    def process_value3(self, value3_str):
        print(f"Valor en process_value3: {value3_str}")
        value3 = self.scan_value(value3_str)
        if value3 is not None:
            print(f"Valor3 procesado: {value3}")
            return value3
        else:
            return None

    def scan_value(self, value_str):
        try:
            value = float(value_str)
            print(f"Valor convertido: {value}")
            return value
        except ValueError:
            print(f"Error al convertir el valor {value_str} a flotante.")
            return None

    def process_shift_register(self, value1, pressure_caj, value2, value3):
        # Simular el Insert Into Array de LabVIEW
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar en los arrays (shift registers simulados)
        self.shift_register_array1.append(value1)
        self.shift_register_array2.append(pressure_caj)
        self.shift_register_array3.append(timestamp)

        # Unir las listas en una matriz y transponerla
        self.shift_register_combined = np.transpose(
            [self.shift_register_array1, self.shift_register_array2, self.shift_register_array3]
        )

        print("Shift Register combinado:")
        print(self.shift_register_combined)
