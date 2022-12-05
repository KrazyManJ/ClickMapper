from dataclasses import dataclass

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QPushButton, QFrame, QLabel

from app import utils, pather
from os.path import dirname,pardir,join as pathjoin

class CMBaseDialog(QDialog):
    BtnClose: QPushButton
    TitleBar: QFrame
    Title: QLabel
    TitleIcon: QFrame

    BtnAccept: QPushButton
    BtnReject: QPushButton
    BtnCancel: QPushButton

    DialogIcon: QFrame
    DialogText: QLabel
    DialogContent: QFrame

    def __init__(self):
        super().__init__()

        self.clickPos = None

        uic.loadUi(pather.ui_design_file("base_dialog.ui"), self)
        self.setWindowTitle("ClickMapper")
        self.setWindowIcon(QIcon(":/favicon/icon.svg"))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        utils.apply_shadow(self, 120, y=0, r=16)
        utils.apply_shadow(self.TitleBar, 80)
        utils.apply_shadow(self.Title, 100)
        utils.apply_shadow(self.TitleIcon, 100, x=2)
        utils.apply_shadow(self.DialogIcon, 80)

        self.BtnClose.clicked.connect(lambda: self.done(0))
        utils.apply_shadow(self.BtnClose, 80)

        self.TitleBar.mousePressEvent = self.TitleBarClick
        self.TitleBar.mouseMoveEvent = self.TitleBarMove
        self.TitleBar.mouseReleaseEvent = self.TitleBarRelease

        self.BtnReject.clicked.connect(lambda: self.done(0))
        self.BtnAccept.clicked.connect(lambda: self.done(1))
        self.BtnCancel.clicked.connect(lambda: self.done(2))

        for b in [self.BtnCancel, self.BtnAccept, self.BtnReject]:
            utils.apply_shadow(b, 80)

    def showIcon(self, state: bool):
        if state:
            self.DialogIcon.show()
            self.DialogContent.layout().setSpacing(20)
        else:
            self.DialogIcon.hide()
            self.DialogContent.layout().setSpacing(0)

    def TitleBarClick(self, ev: QtGui.QMouseEvent):
        self.clickPos = ev.pos()

    def TitleBarMove(self, event):
        if self.clickPos is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.clickPos)

    def TitleBarRelease(self, ev):
        self.clickPos = None

    def execResponse(self):
        result = self.exec_()
        return CMDialogResponseHolder(result == 0, result == 1, result == 2)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.done(1 if a0.isAccepted() else 2)


@dataclass(frozen=True)
class CMDialogResponseHolder:
    rejected: bool
    accepted: bool
    canceled: bool
