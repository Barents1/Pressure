import numpy as np
from PyDAQmx import Task
from PyDAQmx.DAQmxFunctions import DAQmxReadAnalogF64
from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByChannel
from PyDAQmx.DAQmxTypes import int32

from PyDAQmx.DAQmxFunctions import DAQmxWriteDigitalLines
from PyDAQmx.DAQmxFunctions import DAQmxWriteAnalogF64

class AnalogInput(Task):
    def __init__(self, channel, sample_rate=1000, num_samples=100):
        super().__init__()
        self.sample_rate = sample_rate
        self.num_samples = num_samples
        # Configurar el canal de entrada analógica
        self.CreateAIVoltageChan(channel, "", 0, -10.0, 10.0, DAQmx_Val_GroupByChannel, None)
        self.CfgSampClkTiming("", sample_rate, DAQmx_Val_GroupByChannel, DAQmx_Val_GroupByChannel, num_samples)
    
    def read(self):
        # Crear array para almacenar los datos leídos
        data = np.zeros((self.num_samples,), dtype=np.float64)
        read = int32()
        self.ReadAnalogF64(self.num_samples, 10.0, DAQmx_Val_GroupByChannel, data, len(data), read, None)
        return data
    
class AnalogOutput(Task):
    def __init__(self, channel):
        super().__init__()
        #establecer el limite de los rangos
        self.CreateAOVoltageChan(channel, "", 0.0, 5.0, DAQmx_Val_GroupByChannel, None)
    
    def write(self, data):
        DAQmxWriteAnalogF64(self, len(data), False, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

class DigitalOutput(Task):
    def __init__(self, channels):
        super().__init__()
        # Configurar el canal de salida digital
        self.CreateDOChan(channels, "", DAQmx_Val_GroupByChannel)
    
    def write(self, values):
        # values debe ser un array de 0 o 1 (booleanos)
        data = np.array(values, dtype=np.uint8)
        written = int32()
        DAQmxWriteDigitalLines(self, len(data), 1, 10.0, DAQmx_Val_GroupByChannel, data, written, None)