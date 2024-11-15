import numpy as np
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import DAQmx_Val_Volts, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines
from PyDAQmx.DAQmxFunctions import DAQmxWriteAnalogF64, DAQmxReadDigitalU32, DAQmxWriteDigitalU32, DAQmxStartTask, DAQmxStopTask
import ctypes

class AnalogOutput(Task):
    def __init__(self, analog_channel):
        super().__init__()
        self.CreateAOVoltageChan(str(analog_channel), "", 0.0, 5.0, DAQmx_Val_Volts, None)
        self.task_running = False  # Nueva bandera para verificar si la tarea está en ejecución

    def write(self, data):
        data = np.array(data, dtype=np.float64)
        # No se llama a DAQmxStartTask aquí
        DAQmxWriteAnalogF64(self.taskHandle, 1, False, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

    def on_bomb(self, voltage):
        if 0.0 <= voltage <= 5.0:
            if not self.task_running:
                DAQmxStartTask(self.taskHandle)
                self.task_running = True
            self.write([voltage])  
            print(f"Señal analógica activada con {voltage}V")
        else:
            print("Error: El voltaje debe estar entre 0 y 5V")

    def off_bomb(self):
        if self.task_running:
            self.write([0.0])  # Apagar la salida analógica
            DAQmxStopTask(self.taskHandle)  # Detener la tarea solo si estaba en ejecución
            self.task_running = False
            print("Señal analógica desactivada")
        else:
            print("La tarea ya está detenida o no fue iniciada")

    def stop_task(self):
        if self.task_running:
            DAQmxStopTask(self.taskHandle)
            self.task_running = False
        print("Tarea de salida analógica detenida")

class DigitalOutput(Task):
    def __init__(self, digital_channel):
        super().__init__()
        self.CreateDOChan(digital_channel, "", DAQmx_Val_ChanForAllLines)

    def write(self, value):
        # Convierte el valor en un array numpy de tipo uint32
        data = np.array([value], dtype=np.uint32)
        DAQmxWriteDigitalU32(self.taskHandle, 1, True, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

    def activate_valve(self):
        self.write(0b0001)  # Activa la válvula en p0.0

    def activate_motor(self):
        self.write(0b1000)  # Activa el motor en p0.3

    def activate_both(self):
        self.write(0b1001)

    def deactivate_all(self):
        self.write(0b0000)
        print("Todas las líneas desactivadas")

    def stop_task(self):
        DAQmxStopTask(self.taskHandle)
        print("Tarea digital detenida")

    def check_out_digital(self):
        data = np.zeros(1, dtype=np.uint32)
        samps_per_chan_read = ctypes.c_int32()  # Cambiado a un entero de ctypes
        DAQmxReadDigitalU32(
            self.taskHandle,
            1,  # numSampsPerChan
            10.0,  # timeout
            DAQmx_Val_GroupByChannel,
            data,
            len(data),
            ctypes.byref(samps_per_chan_read),  # Usamos byref para pasar un puntero
            None  # reserved
        )
        return data[0] != 0

class ControlDevice:
    def __init__(self):
        analog_channel = "Dev1/ao0"
        digital_channel = "Dev1/port0"
        self.analog_output = AnalogOutput(analog_channel)
        self.digital_output = DigitalOutput(digital_channel)

    def active_valvule(self):
        self.digital_output.activate_both()
        print("Puertos digitales activados")

    def up_pressure(self, voltage):
        self.analog_output.on_bomb(voltage)

    def down_pressure(self):       
        self.analog_output.off_bomb()

    def stop_all_tasks(self):
        self.analog_output.off_bomb()
        self.digital_output.deactivate_all()
        self.analog_output.stop_task()
        self.digital_output.stop_task()

    def check_port_digital(self):
        if self.digital_output.check_out_digital():
            print("Las salidas digitales están activas.")
            return True
        else:
            print("Todas las salidas digitales están desactivadas.")
            return False

# Filtro media Movil
"""
class PIDController:
    def __init__(self, dt, min_output=-100, max_output=100):
        # self.Kp = 0.1
        # self.Ki = 0.002
        # self.Kd = 0.05
        self.Kp = 0.054236
        self.Ki = 0.0010894
        self.Kd = 0.25123
        self.dt = dt
        self.min_output = min_output
        self.max_output = max_output
        self.prev_error = 0
        self.integral = 0
        self.output_history = []  # Lista para el filtro de media móvil
        self.window_size = 5  # Tamaño de la ventana para el filtro de media móvil

    def calculate(self, setpoint, pressure_measured):
        error = setpoint - pressure_measured

        # Término Proporcional
        P = self.Kp * error

        # Término Integral con integración trapezoidal
        self.integral += (error + self.prev_error) / 2 * self.dt
        I = self.Ki * self.integral

        # Término Derivativo
        D = self.Kd * (error - self.prev_error) / self.dt

        # Salida del controlador PID
        output = P + I + D

        # Limitar el valor del output al rango especificado (por ejemplo, -100 a 100)
        output = max(self.min_output, min(self.max_output, output))

        # Escalar el output de -100 a 100 al rango de 0 a 5V
        if error <= 0.5:
            output_ajustado = 0 
        else:
            output_ajustado = (output - self.min_output) / (self.max_output - self.min_output) * 5

        # Aplicar un filtro de media móvil para suavizar la señal
        self.output_history.append(output_ajustado)
        if len(self.output_history) > self.window_size:
            self.output_history.pop(0)
        filtered_output = sum(self.output_history) / len(self.output_history)

        self.prev_error = error
        return filtered_output, error
"""
#Filtro Exponencial Suavizado
class PIDController:
    def __init__(self, dt, min_output=-100, max_output=100):
        self.Kp = 0.1
        self.Ki = 0.002
        self.Kd = 0.05
        # self.Kp = 0.054236
        # self.Ki = 0.0010894
        # self.Kd = 0.25123
        self.dt = dt
        self.min_output = min_output
        self.max_output = max_output
        self.prev_error = 0
        self.integral = 0
        self.filtered_output = 0  # Salida filtrada inicial
        self.alpha = 0.2  # Factor de suavizado para el filtro exponencial
        self.umbral_positivo = 4  # Define un valor por defecto o pásalo como parámetro
        self.umbral_negativo = -4
        
        self.filtro_activo = False
        self.umbral_filtro = 10  # Ajustar este umbral según sea necesario

        self.antiwindup_limit = 50

    def calculate(self, setpoint, pressure_measured):
        error = setpoint - pressure_measured

        # Término Proporcional
        P = self.Kp * error

        # Término Integral con integración trapezoidal
        self.integral += (error + self.prev_error) / 2 * self.dt
        self.integral = max(-self.antiwindup_limit, min(self.integral, self.antiwindup_limit))
        I = self.Ki * self.integral

        # Término Derivativo
        D = self.Kd * (error - self.prev_error) / self.dt

        # Salida del controlador PID
        output = P + I + D

        # Limitar el valor del output al rango especificado (por ejemplo, -100 a 100)
        output = max(self.min_output, min(self.max_output, output))
        output_ajustado = (output - self.min_output) / (self.max_output - self.min_output) * 5

        # Lógica de activación del filtro
        if self.umbral_positivo >= error >= self.umbral_negativo:
            self.filtro_activo = True

        # Aplicar el filtro solo si está activo
        if self.filtro_activo:
            self.filtered_output = self.alpha * output_ajustado + (1 - self.alpha) * self.filtered_output
        else:
            self.filtered_output = output_ajustado

        if self.filtro_activo:
            print("filtro activado")
        else:
            print("filtro desactivado")

        self.prev_error = error
        return self.filtered_output, error