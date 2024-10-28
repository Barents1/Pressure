"""
version: 1.00, fecha : 02/09/2024
class main
Copyright. INAMHI <www.inamhi.gob.ec>. Todos los derechos reservados.
"""
from PyQt5 import QtWidgets
from gui.gui_main import *
from ui_manager import UIManager
from connection import ConnectionManager

class MainMenu(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.ui_manager = UIManager(self)
        self.connection = ConnectionManager(self, self.ui_manager)
        self.connection.load_port()
        self.ui_manager.initialize_ui()
        self.initialize_actions()
        self.disable_button()
        self.time_enable = True

    def initialize_actions(self):
        self.cbx_conn.activated.connect(self.connection.check_port)
        self.btn_save_rute.clicked.connect(self.ui_manager.save_rute)
        self.btn_connect.clicked.connect(self.connection.connect_device)
        self.btn_start.clicked.connect(self.connection.start_device)
        self.btn_stop_conn.clicked.connect(self.connection.close_bomb)
        self.btn_start_conn.clicked.connect(self.connection.set_point)
        self.btn_enable.clicked.connect(self.ui_manager.toggle_button_state)
        self.btn_time_duration.clicked.connect(self.ui_manager.toggle_button_time_state) 
        self.btn_reset.clicked.connect(self.reset_value)    
        self.btn_finish_system.clicked.connect(self.connection.close_bomb)
        self.btn_save_ctrl_data.clicked.connect(self.connection.change_num_chk)
        self.btn_stop_ctrl_data.clicked.connect(self.connection.stop_data_saving)

    def enable_button(self):
        self.inp_a0.setEnabled(True)
        self.inp_a1.setEnabled(True)

    def disable_button(self):
        self.inp_a0.setEnabled(False)
        self.inp_a1.setEnabled(False)

    def enable_time(self):
        self.inp_time_duration.setEnabled(True)
        self.time_enable = True

    def disable_time(self):
        self.inp_time_duration.setEnabled(False)
        self.time_enable = False

    def reset_value(self):
        pa_a0, pa_a1 = self.connection.get_value_reset()
        self.inp_a0.setValue(pa_a0)
        self.inp_a1.setValue(pa_a1)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

"""
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
        #establecer el limite de los rangos 0 - 5V
        self.CreateAOVoltageChan(channel, "", 0.0, 5.0, DAQmx_Val_GroupByChannel, None)

    def write(self, data):
        DAQmxWriteAnalogF64(self, len(data), False, 10.0, DAQmx_Val_GroupByChannel, data, None, None)

    def on_bomb(self):
        self.write(np.array([4.0]))  # Activa el relé enviando 5V

    def off_bomb(self):
        self.write(np.array([0.0]))  # Desactiva el relé enviando 0V

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
		
if __name__ == "__main__":
    # leer datos analogicos
	channels = [f"Dev1/ai{i}" for i in range(0, 4)]
	channel_data = {channel: [] for channel in channels}
    start_time = time.time()

    while time.time() - start_time < 10:  # Loop durante 10 segundos
        for channel in channels:
            analog_input = AnalogInput(channel)
            analog_input.start()
            
            data = analog_input.read()
            channel_data[channel].append(data)
            
            analog_input.stop()
            analog_input.clear()
            
        time.sleep(0.1) 

    for channel, data_list in channel_data.items():
        print(f"Datos leídos en {channel}: {data_list}")
		
	# escribir datos analogicos
            
	channelOUT = "Dev1/ao0"
	#analog_output = AnalogOutput(channelOUT)
	#analog_output.on_bomb()
	#time.sleep(4)
	#analog_output.off_bomb()
	#analog_output.stop()
	#analog_output.clear()
"""