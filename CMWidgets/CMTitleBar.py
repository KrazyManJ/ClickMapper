import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QPushButton
from qframelesswindow.utils import startSystemMove

import Utils
from Utils import apply_shadow


class CMTitleBar(QWidget):
    TitleBar: QFrame
    Title: QLabel
    BtnClose: QPushButton
    BtnMin: QPushButton
    BtnMax: QPushButton
    TitleIcon: QFrame
    MacroName: QLabel

    def __init__(self, parent):
        super().__init__(parent)  # type: ignore
        uic.loadUi("ui/titlebar.ui", self)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.macroname = ""

        BTN_MAP = [(self.BtnClose, self.window().close), (self.BtnMin, self.window().showMinimized),
                   (self.BtnMax, self.__toggleMaxState)]
        for widg, fct in BTN_MAP:
            widg.clicked.connect(fct)
            apply_shadow(widg, 80)

        apply_shadow(self, 80)
        apply_shadow(self.Title, 100)
        apply_shadow(self.TitleIcon, 100, x=2)

        self.window().installEventFilter(self)

    def setMacroTitling(self, title):
        self.macroname = title
        self.updateMacroTitling()
        self.MacroName.setToolTip(self.macroname)

    def updateMacroTitling(self):
        self.MacroName.setText(Utils.crop_string(self.macroname, (self.window().width() - 500) // 10))

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
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def _isDragRegion(self, pos):
        return 0 < pos.x() < self.width() - 46 * 3

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.updateMacroTitling()
