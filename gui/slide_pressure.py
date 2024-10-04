from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor

class TankGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.draw_tank()

    def draw_tank(self):
        tank_rect = QRectF(0, 0, 300, 50)  # Tank dimensions (width x height)
        tank_item = QGraphicsRectItem(tank_rect)
        tank_item.setBrush(QBrush(QColor(200, 200, 255)))  # Light blue color for the tank
        tank_item.setPen(QPen(Qt.NoPen))  # No border
        
        # Create a water level
        self.water_level = QGraphicsRectItem(0, 0, 0, 50)  # Initial water level (width x height)
        self.water_level.setBrush(QBrush(QColor(0, 0, 255)))  # Blue color for water
        self.water_level.setPen(QPen(Qt.NoPen))  # No border
        
        self.scene.addItem(tank_item)
        self.scene.addItem(self.water_level)

    def update_water_level(self, value):
        min_value = 500
        max_value = 1100
        max_width = 300
        min_width = 0

        width = (value - min_value) / (max_value - min_value) * max_width
        width = max(min_width, min(width, max_width))
        self.water_level.setRect(0, 0, width, 50)  # Set the new width of the water level

class SliderExample(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        
        # Create and set up the slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(500)
        self.slider.setMaximum(1100)
        self.slider.setValue(500)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(100)
        
        # Create and set up the label
        self.label = QLabel("Valor: 500")
        
        # Create and set up the tank graphics view
        self.tank_view = TankGraphicsView()
        self.tank_view.setFixedSize(320, 70)  # Size of the tank view (width x height)
        
        # Connect slider value change to update the tank water level
        self.slider.valueChanged.connect(self.update_label_and_tank)
        
        # Add widgets to layout
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        layout.addWidget(self.tank_view)
        
        self.setLayout(layout)

    def update_label_and_tank(self, value):
        self.label.setText(f"Valor: {value}")
        self.tank_view.update_water_level(value)

if __name__ == '__main__':
    app = QApplication([])
    window = SliderExample()
    window.show()
    app.exec_()