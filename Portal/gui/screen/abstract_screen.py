from PyQt4 import QtGui
from PyQt4.QtGui import *


class AbstractScreen(QtGui.QWidget):
    width = 320
    height = 240

    def __init__(self, title: str):
        super(AbstractScreen, self).__init__()
        self._title = title
        self.vbox= None
        self.frame = 0
        self._set_layout()
        self.initUI()
        self.show()

    def _set_layout(self):
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addStretch(1)
        self.grid = QtGui.QGridLayout()
        self.before_vertical_layout(self.vbox)
        self.vbox.addLayout(self.grid, 0)

    def before_vertical_layout(self,vbox):
        pass

    def refresh(self):
        self.frame += 1

    def initUI(self):
        self.setGeometry(0, 0, AbstractScreen.width, AbstractScreen.height)
        self.setStyleSheet("background: #222")

    def add_button(self, name: str, x: int, y: int, handler=None)->QPushButton:
        btn = QPushButton(name)
        btn.resize(btn.sizeHint())
        btn.setStyleSheet(
            "background:#EEE; border:#000; color:#000; padding:1em")
        if handler is not None:
            btn.clicked.connect(handler)
        self.grid.addWidget(btn, y, x)
        return btn
