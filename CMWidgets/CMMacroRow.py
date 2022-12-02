import os.path

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QPushButton, QLabel, QVBoxLayout

from typing import TYPE_CHECKING

from Macro import Macro

if TYPE_CHECKING:
    from CMWidgets.CMWindow import CMWindow


class CMMacroRow(QFrame):
    label: QLabel
    button: QPushButton

    def __init__(self, ui: "CMWindow", macro_path:str, parent=None, title="none", author="unknown"):
        super().__init__(parent)

        self.win = ui
        self.macro_path = macro_path

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)

        self.label_layout = QVBoxLayout(self)
        self.label_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel()
        self.label.setText(title)
        self.label_layout.addWidget(self.label)

        self.author = QLabel()
        self.author.setText(author)
        self.author.setStyleSheet('color: #aaaaaa;font: 12pt "Inter"')
        self.label_layout.addWidget(self.author)

        self.main_layout.addLayout(self.label_layout)

        self.button = QPushButton(self)
        self.button.clicked.connect(self.removeMacro)
        self.main_layout.addWidget(self.button)

    def isValidPath(self):
        if not os.path.isfile(self.macro_path): return False
        return Macro.is_macro_json(open(self.macro_path,"r",encoding="utf8",errors="surrogateescape"))

    def mousePressEvent(self, a0) -> None:
        self.win.macroChoose(self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        print("Double Click")

    def removeMacro(self):
        self.win.macroDelete(self)