import sys
import ctypes

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic  # type: ignore
from qframelesswindow.utils import startSystemMove

import src.src # type: ignore
from qframelesswindow import FramelessWindow, TitleBar

App = QApplication(sys.argv)


def applyShadow(widget: QWidget, alpha, x=0, y=4, r=8):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(r)
    shadow.setYOffset(y)
    shadow.setXOffset(x)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)

class UITitle(QWidget):

    TitleBar: QFrame
    Title: QLabel
    BtnClose: QPushButton
    BtnMin: QPushButton
    BtnMax: QPushButton
    TitleIcon: QFrame

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/titlebar.ui", self)

        self.setAttribute(Qt.WA_StyledBackground, True)

        for widg, fct in [
            (self.BtnClose, self.window().close),
            (self.BtnMin, self.window().showMinimized),
            (self.BtnMax, self.__toggleMaxState)
        ]:
            widg.clicked.connect(fct)
            applyShadow(widg,80)

        applyShadow(self,80)
        applyShadow(self.Title, 100)
        applyShadow(self.TitleIcon, 100, x=2)

        self.window().installEventFilter(self)

    def eventFilter(self, obj, e):
        return super().eventFilter(obj, e)

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton: return
        self.__toggleMaxState()

    def mouseMoveEvent(self, e):
        if sys.platform != "win32" or not self._isDragRegion(e.pos()): return
        startSystemMove(self.window(), e.globalPos())

    def mousePressEvent(self, e):
        if sys.platform == "win32" or e.button() != Qt.LeftButton or not self._isDragRegion(e.pos()): return
        startSystemMove(self.window(), e.globalPos())

    def __toggleMaxState(self):
        if self.window().isMaximized(): self.window().showNormal()
        else: self.window().showMaximized()

    def _isDragRegion(self, pos):
        return 0 < pos.x() < self.width() - 46 * 3



class UI(FramelessWindow):


    def __init__(self) -> None:
        super().__init__()
        self.clickPosition = QPoint(0,0)
        self.normalWindowWidth = None
        uic.loadUi("ui/design.ui", self)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.ClickMapper.1.0.0")
        self.setWindowIcon(QIcon(":/favicon/icon.svg"))
        self.setTitleBar(UITitle(self)) # type: ignore
        self.titleBar.raise_()


if __name__ == '__main__':
    ui = UI()
    ui.show()
    sys.exit(App.exec())
