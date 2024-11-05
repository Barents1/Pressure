import numpy as np
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import DAQmx_Val_Volts, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines
from PyDAQmx.DAQmxFunctions import DAQmxWriteAnalogF64, DAQmxWriteDigitalU32, DAQmxStartTask, DAQmxStopTask

class AnalogOutput(Task):
    def __init__(self, analog_channel):
        super().__init__()
        # Configuración del canal de salida analógica (0 a 5V)
        self.CreateAOVoltageChan(str(analog_channel), "", 0.0, 5.0, DAQmx_Val_Volts, None)

    def write(self, data):
        data = np.array(data, dtype=np.float64)
        DAQmxWriteAnalogF64(self.taskHandle, 1, False, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

    def on_bomb(self, voltage):
        if 0.0 <= voltage <= 5.0:
            DAQmxStartTask(self.taskHandle)
            self.write([voltage])  # Activa la señal analógica con el voltaje dado
            print(f"Señal analógica activada con {voltage}V")
        else:
            print("Error: El voltaje debe estar entre 0 y 5V")

    def off_bomb(self):
        self.write([0.0])  # Desactiva la señal analógica enviando 0V
        print("Señal analógica desactivada")

    def stop_task(self):
        DAQmxStopTask(self.taskHandle)
        print("Tarea de salida analógica detenida")

class DigitalOutput(Task):
    def __init__(self, digital_channel):
        super().__init__()
        # Configuración del canal de salida digital
        self.CreateDOChan(digital_channel, "", DAQmx_Val_ChanForAllLines)

    def write(self, value):
        # Convierte el valor en un array numpy de tipo uint32
        data = np.array([value], dtype=np.uint32)
        DAQmxWriteDigitalU32(self.taskHandle, 1, True, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

    def activate_valve(self):
        self.write(0b0001)  # Activa la válvula en p0.0
        print("Válvula de sellado activada")

    def activate_motor(self):
        self.write(0b1000)  # Activa el motor en p0.3
        print("Motor activado")

    def activate_both(self):
        self.write(0b1001)
        print("Válvula y motor activados")

    def deactivate_all(self):
        self.write(0b0000)
        print("Todas las líneas desactivadas")

    def stop_task(self):
        DAQmxStopTask(self.taskHandle)
        print("Tarea digital detenida")

class Control:
    def __init__(self):
        analog_channel = "Dev1/ao0"
        digital_channel = "Dev1/port0"
        self.analog_output = AnalogOutput(analog_channel)
        self.digital_output = DigitalOutput(digital_channel)

    def up_pressure(self, voltage):
        self.digital_output.activate_both()
        self.analog_output.on_bomb(voltage)

    def down_pressure(self):
        self.digital_output.activate_both()
        self.analog_output.off_bomb() 

    def stop_all_tasks(self):
        self.analog_output.off_bomb()
        self.digital_output.deactivate_all()
        self.analog_output.stop_task()
        self.digital_output.stop_task()

# if __name__ == "__main__":
#     import time
#     control = Control()

#     # Prueba de las funciones de control
#     control.up_pressure(2.0)  # Enviar 2V de señal analógica
#     time.sleep(10)

#     control.down_pressure()  # Activar válvula y motor
#     time.sleep(5)
#     control.stop_all_tasks() 