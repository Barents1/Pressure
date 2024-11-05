import numpy as np
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import DAQmx_Val_Volts, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines
from PyDAQmx.DAQmxFunctions import DAQmxWriteAnalogF64, DAQmxWriteDigitalU32, DAQmxStartTask, DAQmxStopTask

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
        if not self.task_running:
            DAQmxStartTask(self.taskHandle)
            self.task_running = True
        self.write([0.0])
        if self.task_running:
            DAQmxStopTask(self.taskHandle)
            self.task_running = False
        print("Señal analógica desactivada")

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

class ControlDevice:
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