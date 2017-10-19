import math

from PyQt4.QtGui import QPainter
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtGui, QtCore


class BootScreen(AbstractScreen):
    width = 320
    height = 240

    def __init__(self):
        super(BootScreen, self).__init__("Booting")

    def refresh(self):
        super(BootScreen, self).refresh()
        self.repaint()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_lines(qp)
        qp.end()

    def get_pen_color(self, offset):
        pos = self.frame + offset
        r = 255 * ((math.sin(pos / 20) + 1) / 2)
        g = 255 * ((math.sin(pos / 20 + (math.pi / 2)) + 1) / 2)
        b = 255 * ((math.sin(pos / 20 + math.pi) + 1) / 2)

        # Fade in.
        if self.frame < 50:
            r = self.fade_color(r)
            g = self.fade_color(g)
            b = self.fade_color(b)
        return QtGui.QColor(r, g, b)

    def fade_color(self, color):
        if self.frame < 50:
            temp = self.frame / 50
            color *= temp
        return color

    def draw_box(self, qp: QtGui.QPen, pos: float, size: float,
                 h_squeeze: float, x: int, y: int):
        pi_part = math.pi / 2
        for i in range(0, 4):
            part_offset = pi_part * i
            x1 = x + math.sin(pos + part_offset) * size
            x2 = x + math.sin(pos + part_offset + pi_part) * size
            y1 = y + math.cos(pos + part_offset) * size * h_squeeze
            y2 = y + math.cos(pos + part_offset + pi_part) * size * h_squeeze
            qp.drawLine(x1, y1, x2, y2)

    def draw_lines(self, qp):
        slowdown = 20
        pos = self.frame / slowdown
        h_squeeze = 0.5

        color_temp = self.fade_color(255)
        color = QtGui.QColor(color_temp, color_temp, color_temp)
        qp.setPen(color)
        qp.setFont(QtGui.QFont('Decorative', 20))
        qp.drawText(125, 110, 320, 240, QtCore.Qt.AlignLeft, "MonitoringBox")

        font = QtGui.QFont('Decorative', 10)
        font.setItalic(True)
        qp.setFont(font)
        qp.drawText(128, 135, 320, 240, QtCore.Qt.AlignLeft,
                    "Booting" + ("." * (int(self.frame / 10) % 4)))

        slowdown = 20

        for i in range(0, 12):
            pen = QtGui.QPen(self.get_pen_color(i), 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setRenderHint(QPainter.Antialiasing)
            size = 30 + (math.sin((self.frame + i * 6) / slowdown) * 25)
            self.draw_box(qp, pos, size, h_squeeze, 60, 100 + i * 6)
