from PyQt4 import QtGui


class AbstractScreen(QtGui.QWidget):
    width = 320
    height = 240

    def __init__(self, title: str):
        super(AbstractScreen, self).__init__()
        self._title = title
        self.pre_init()
        self.initUI()
        self.frame = 0

    def pre_init(self):
        pass

    def refresh(self):
        self.frame += 1

    def initUI(self):
        self.setGeometry(0, 0, AbstractScreen.width, AbstractScreen.height)
        self.show()
        self.setStyleSheet("background: #000")
