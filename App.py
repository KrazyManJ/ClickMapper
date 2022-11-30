import sys
import ctypes

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic  # type: ignore

from qframelesswindow import FramelessWindow

import src.src  # type: ignore
from RichPresence import RichPressence
from CMTitleBar import CMTitleBar

App = QApplication(sys.argv)


class CMWindow(FramelessWindow):

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.clickPosition = QPoint(0, 0)

        uic.loadUi("ui/design.ui", self)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.ClickMapper.1.0.0")
        self.setWindowIcon(QIcon(":/favicon/icon.svg"))
        self.setTitleBar(CMTitleBar(self))  # type: ignore
        self.titleBar.raise_()

        frameGm = self.frameGeometry()
        frameGm.moveCenter(self.app.desktop().screenGeometry(
            self.app.desktop().screenNumber(self.app.desktop().cursor().pos())).center())
        self.move(frameGm.topLeft())
        RichPressence.begin()

    def setMacroTitling(self, title: str):
        self.setWindowTitle(f"Click Mapper - {title}")
        self.titleBar.setMacroTitling(title)
        RichPressence.setMacroName(title)

    def closeEvent(self, a0: QCloseEvent) -> None:
        RichPressence.close()


if __name__ == '__main__':
    ui = CMWindow(App)
    ui.show()
    ui.setMacroTitling("my_first_long_name_and_ultra_cool_macro.py")  # For testing
    sys.exit(App.exec())
