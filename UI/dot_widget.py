from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget


class DotWidget(QWidget):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.setGeometry(int(size/2), int(size/2), size, size)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Anti-aliasing per un bordo più fluido

        painter.setBrush(QColor(8, 155, 204))

        painter.setPen(Qt.NoPen)  # Nasconde il pennello del contorno
        painter.drawEllipse(0, 0, self.size, self.size)
