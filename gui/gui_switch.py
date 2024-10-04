from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout
from PyQt5.QtCore import Qt

class SwitchButton(QPushButton):
    def __init__(self, parent=None):
        super(SwitchButton, self).__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(60, 30)
        self.setStyleSheet(self.switch_style(False))
        self.setText("Off")
        self.clicked.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet(self.switch_style(True))
            self.setText("On")
        else:
            self.setStyleSheet(self.switch_style(False))
            self.setText("Off")

    def switch_style(self, checked):
        if checked:
            return '''
                QPushButton {
                    background-color: #4caf50;
                    border-radius: 15px;
                    border: 1px solid #000;
                }
            '''
        else:
            return '''
                QPushButton {
                    background-color: #ccc;
                    border-radius: 15px;
                    border: 1px solid #000;
                }
            '''