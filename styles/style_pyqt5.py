from PyQt5 import QtCore, QtGui

class Style:
    LOGO_SIZE = QtCore.QSize(107, 50)
    BUTTON_SIZE = QtCore.QSize(80, 25)
    COMBO_SIZE = QtCore.QSize(300, 30)
    WINDOW_SIZE_MAIN = QtCore.QSize(700, 450)

    FONT_FAMILY = 'Times New Roman'
    FONT_SIZE_TITLE = 15
    FONT_SIZE_TITLE_INSTRUCTION = 13
    FONT_SIZE_SUB_INSTRUCTION = 11
    FONT_SIZE_BUTTON = 11
    FONT_WEIGHT = QtGui.QFont.Bold

    @staticmethod
    def set_window_size(window, size_key):
        sizes = {
            'main': Style.WINDOW_SIZE_MAIN
        }
        if size_key in sizes:
            window.setFixedSize(sizes[size_key])

    @staticmethod
    def combo_size_device_styles(components):
        for component in components:
            component.setMinimumSize(Style.COMBO_SIZE)

    @staticmethod
    def img_size_logo_styles(components):
        for component in components:
            component.setMinimumSize(Style.LOGO_SIZE)

    @staticmethod
    def label_title_styles(labels):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_TITLE, Style.FONT_WEIGHT)
        for label in labels:
            label.setFont(font)

    @staticmethod
    def label_title_instruction_styles(labels):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_TITLE_INSTRUCTION, Style.FONT_WEIGHT)
        for label in labels:
            label.setFont(font)

    @staticmethod
    def label_sub_instructiol_styles(labels):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_SUB_INSTRUCTION)
        for label in labels:
            label.setFont(font)

    @staticmethod
    def button_primary_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #007bff;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #0b7dda;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)

    @staticmethod
    def button_warning_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #ff9800;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #e68a00;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)

    @staticmethod
    def button_success_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #04AA6D;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #46a049;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)

    @staticmethod
    def button_secondary_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #6D214F;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)

    @staticmethod
    def button_disabled_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #808080;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #808080;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)

    @staticmethod
    def button_danger_style(buttons):
        font = QtGui.QFont(Style.FONT_FAMILY, Style.FONT_SIZE_BUTTON)
        button_style = """
            QPushButton {
                background-color: #f44336;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #da190b;
            }
        """
        for button in buttons:
            button.setMinimumSize(Style.BUTTON_SIZE)
            button.setFont(font)
            button.setStyleSheet(button_style)
    
    @staticmethod
    def stacked_widget_bgd_style(stacked_widget):
        for stacked in stacked_widget:
            stacked.setStyleSheet("background-color: #cce8f5;")

    @staticmethod
    def frame_bgd_styles(frames):
        for frame in frames:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #cce8f5;
                }
            """)

    @staticmethod    
    def frame_bgd_white_styles(widget):
        for component in widget:    
            component.setStyleSheet("background-color: white;")

    @staticmethod  
    def window_bgd_styles(widget):
        for component in widget:    
            component.setStyleSheet("background-color: #cce8f5;")