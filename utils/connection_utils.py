from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
import serial
import serial.tools.list_ports
import os

class ConnectionUtils:
    def __init__(self):
        self.conn_bomb = None
        self.desktop_path = Path.home() / "Desktop"
        self.new_folder = self.desktop_path / "Presion"

    def load_port(self, combo):
        ports = serial.tools.list_ports.comports()
        combo.clear()
        if not ports:
            combo.addItem("No hay puertos disponibles")
        else:
            for port in ports:
                combo.addItem(port.device)

    def check_port(self, combobox):
        selected_port = combobox.currentText()

        ports = serial.tools.list_ports.comports()
        if selected_port and ports:
            puerto_info = next((port for port in ports if port.device == selected_port), None)
            if puerto_info:
                mensaje = f"Información del Puerto Seleccionado ({selected_port}):\n"
                mensaje += f"Dispositivo: {puerto_info.device}\n"
                mensaje += f"Nombre: {puerto_info.name}\n"
                mensaje += f"Descripción: {puerto_info.description}\n"
                mensaje += f"ID de hardware: {puerto_info.hwid}\n"
                mensaje += f"PID: {puerto_info.pid}\n"
                mensaje += f"Número de serie: {puerto_info.serial_number}\n"
                mensaje += f"Ubicación: {puerto_info.location}\n"
                mensaje += f"Fabricante: {puerto_info.manufacturer}\n"
                mensaje += f"Producto: {puerto_info.product}\n"
                mensaje += f"Interfaz: {puerto_info.interface}\n"
                QMessageBox.warning(None, "Advertencia", mensaje)
            else:
                mensaje = f"No se encontró información para el puerto seleccionado: {selected_port}"
        else:
            mensaje = "No se encontraron puertos seriales o no se seleccionó ningún puerto."

    def open_folder_dialog(self, parent_widget):
        folder_path = QFileDialog.getExistingDirectory(parent_widget, "Seleccionar Carpeta")
        if folder_path:
            return folder_path.replace('/', '\\')
        return None
    
    def read_or_create_file(self, file_name):
        file_path = os.path.join(os.getcwd(), file_name)

        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('')

        with open(file_path, 'r') as file:
            content = Path(file.read())

        if not content.exists():
            content = str(self.new_folder)
            self.new_folder.mkdir(parents=True, exist_ok=True)

        content = str(content)
        return file_path, content

    def save_rute_to_file(self, file_name, folder_path):
        file_path, _ = self.read_or_create_file(file_name)

        with open(file_path, 'w') as file:
            file.write(folder_path)

    def connection_bomb_util(self, combobox):
        selected_port = combobox.currentText()

        if not selected_port or "No hay puertos disponibles" in selected_port:
            QtWidgets.QMessageBox.critical(
                None, "Error", f"Error: No se ha seleccionado un puerto válido."
            )
            return False

        try:
            self.conn_bomb = serial.Serial(
                port=selected_port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=10,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )

            if self.conn_bomb.is_open:
                QtWidgets.QMessageBox.information(
                    None, "Advertencia", f"Conectado correctamente con el fluke en {selected_port}"
                )
                return self.conn_bomb

        except serial.SerialException as e:
            QtWidgets.QMessageBox.critical(
                None, "Error", f"Error al intentar conectar con la bomba en {selected_port}: {e})"
            )
            return None

        return None

    def close_connection(self):
        if self.conn_bomb and self.conn_bomb.is_open:
            self.conn_bomb.close()
            self.conn_bomb = None
            QtWidgets.QMessageBox.information(
                None, "Informacion", f"Conexión cerrada correctamente."
            )
            return self.conn_bomb