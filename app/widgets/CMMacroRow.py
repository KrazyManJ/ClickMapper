import os.path

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QPushButton, QLabel, QVBoxLayout

from typing import TYPE_CHECKING

from app import utils
from app.widgets.dialogs.CMRemoveMacroDialog import CMRemoveMacroDialog
from app.macro.Macro import Macro

if TYPE_CHECKING:
    from app.widgets.CMWindow import CMWindow


class CMMacroRow(QFrame):
    label: QLabel
    button: QPushButton

    def __init__(self, ui: "CMWindow", macro_path:str, macro: Macro):
        super().__init__(None)

        self.win = ui
        self.macro_path = macro_path
        self.macro = macro

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)

        self.label_layout = QVBoxLayout(self)
        self.label_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel()
        self.label.setText(utils.crop_string(self.macro.name or "Untitled", 25))
        self.label_layout.addWidget(self.label)

        self.author = QLabel()
        self.author.setText(utils.crop_string(self.macro.description or "No description provided", 80))
        self.author.setWordWrap(True)
        self.author.setStyleSheet('color: #777777;font: 9pt "Inter"')
        self.label_layout.addWidget(self.author)

        self.main_layout.addLayout(self.label_layout)

        self.button = QPushButton(self)
        self.button.clicked.connect(self.removeMacro)
        self.main_layout.addWidget(self.button)

    def mousePressEvent(self, a0) -> None:
        if a0.modifiers() & Qt.ControlModifier and a0.button() == Qt.LeftButton:
            os.system(f"explorer /select,{self.macro_path}")
        else:
            self.win.choose_saved_macro(self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.win.run_macro_from_row(self)

    def removeMacro(self):
        dialog = CMRemoveMacroDialog(self.macro.name)
        if dialog.execResponse().accepted:
            self.win.remove_saved_macro(self)