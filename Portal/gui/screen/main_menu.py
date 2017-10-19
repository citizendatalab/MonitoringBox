from PyQt4 import QtGui
from PyQt4.QtGui import *
from gui.screen.abstract_screen import AbstractScreen


class Window(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.button = QtGui.QPushButton('Test', self)
        self.button.clicked.connect(self.handleButton)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.button)

    def handleButton(self):
        print('Hello World')


class MainMenu(QWidget):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.resize(320, 240)
        self.setGeometry(0, 0, AbstractScreen.width, AbstractScreen.height)

        btn = QPushButton('Click me', self)
        btn.resize(btn.sizeHint())
        btn.move(100, 80)
        self.show()

    def refresh(self):
        pass
