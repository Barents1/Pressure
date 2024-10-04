from PyQt5 import QtWidgets

class ComunicacionPid:
    def __init__(self):
        self.ErrApag = -0.258
        self.t_muestreo = 1228
        
        # constantes PID
        self.KP = 0.054236
        self.KI = 0.0010894
        self.KD = 0.25123  # Cambié KP por KD ya que parece que fue un error en tu código

        # Límites
        self.L_min = 86
        self.L_max = 86

        # Variables de proceso
        self.ui_previus = 1100
        self.set_point = 1100
        self.proccess_variable = 1100.52

        self.range = [550, 650, 730, 850, 950, 1050]

        # Inicializando variables de control
        self.proportional = None
        self.error = None
        self.GI = None
        self.GD = None
        self.PIDT = None
        self.voltage_AO0 = None
        self.num_100 = None

        self.stop = False  # Variable de control para detener el loop

    def control_loop(self):
        while not self.stop:
            # Condición principal (botón) que sería el "Case Selector" en LabVIEW
            if True:  # Suponiendo que el selector está en True, puedes reemplazarlo por tu botón
                # While loop secundario
                while True:
                    # Igual a 0? (Equal To 0? Function)
                    condition_igual_0 = (self.ui_previus == 0)

                    # Select Function: condición con salida s? t:f
                    salida_select = 1 if condition_igual_0 else self.ErrApag

                    # Camino 1: Greater Or Equal? (x >= y)
                    condition_geq = (salida_select >= -1)

                    # Camino 2: Less Or Equal? (x <= y)
                    condition_leq = (salida_select <= 0)

                    # And Function (x .and. y)
                    condition_and = condition_geq and condition_leq

                    # Select Function final con salida s? t:f
                    resultado_select = 1 if condition_and else 0

                    # Add Function: suma con el resultado del select y valor inicial del loop
                    resultado_suma = resultado_select + 0

                    # Comparación: Greater Or Equal? con valor 30
                    condition_final_geq = (resultado_suma >= 30)

                    # Or Function con condición final y un botón STOP
                    stop_condition = condition_final_geq or self.stop  # PRINCIPAL es el botón STOP

                    # Condición de salida (similar al stop if true)
                    if stop_condition:
                        break  # Sale del while secundario

                    # Si no, continúa la operación
                    not_condition = not stop_condition

                    # Bundle Function simulada con indicadores (LEDs)
                    led_1 = not_condition
                    led_2 = not_condition

                    # Actualizar LEDs
                    self.update_leds(led_1, led_2)

    def update_leds(self, led_1, led_2):
        # Esta función actualizaría los LEDs en la interfaz gráfica
        print(f"LED 1: {'ON' if led_1 else 'OFF'}, LED 2: {'ON' if led_2 else 'OFF'}")

    def stop_loop(self):
        # Método para detener el bucle
        self.stop = True

#pid_control = ComunicacionPid()
#pid_control.control_loop()
"""
from PyQt5 import QtWidgets
import numpy as np

class ComunicacionPid:
    def __init__(self):
        self.ErrApag = -0.258
        self.t_muestreo = 1228
        self.KP = 0.054236
        self.KI = 0.0010894
        self.KD = 0.25123

        self.L_min = 86
        self.L_max = 86

        self.ui_previus = 1100
        self.set_point = 1100
        self.process_variable = 1100.52

        self.range = [550, 650, 730, 850, 950, 1050]

        self.proportional = None
        self.error = None
        self.GI = None
        self.GD = None
        self.PIDT = None
        self.voltage_AO0 = None
        self.num_100 = None

    def control_loop(self, stop_button, stop_principal):
        """Simulación del Case Structure con un While Loop secundario."""

        # Inicialización de variables
        result_add = 0
        
        while True:
            # Comparar si ErrApag es igual a 0 (Equal To 0? en LabVIEW)
            if self.ErrApag == 0:
                select_value = 1
            else:
                select_value = self.ErrApag

            # Comparaciones Greater Or Equal y Less Or Equal en LabVIEW
            and_condition = (select_value >= -1) and (select_value <= 0)

            # Usar la función Select para elegir entre 1 o 0 (si la condición AND es True)
            selected_value = 1 if and_condition else 0

            # Sumar el valor resultante al valor inicial
            result_add += selected_value

            # Verificar si el resultado es >= 30
            greater_equal_30 = result_add >= 30

            # Condición para detener el loop (botón stop o resultado mayor o igual a 30)
            stop_condition = stop_button or stop_principal or greater_equal_30

            if stop_condition:
                break

            # Simulación de actualización del valor de LEDs (representado con print)
            led_state = not stop_condition
            led_indicator_1 = led_state
            led_indicator_2 = led_state

            # Salida de los LEDs
            print(f"LED 1: {'ON' if led_indicator_1 else 'OFF'}, LED 2: {'ON' if led_indicator_2 else 'OFF'}")

        print("Loop terminado")

# Ejemplo de uso
pid_control = ComunicacionPid()
pid_control.control_loop(stop_button=False, stop_principal=False)
"""