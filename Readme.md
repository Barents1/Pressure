# Librerias Necesarias
pip install pyserial
pip install PyQt5
pip install pyinstaller

python.exe -m pip install --upgrade pip
# Libreria DAQ USB 6212
pip install PyDAQmx
pip install nidaqmx

# Entorno Virtual
# instalar
pip install virtualenv
#   crear
python -m venv venv
#   activar
venv\Scripts\activate
#   desactivar
deactivate
# Obtener Requerimientos
pip install -r requirements.txt