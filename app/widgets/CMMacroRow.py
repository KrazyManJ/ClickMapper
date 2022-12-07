import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QFileDialog

from typing import TYPE_CHECKING

from app import utils
from app.file_manager import CMFile
from app.widgets.dialogs.CMRemoveMacroDialog import CMRemoveMacroDialog
from app.macro.Macro import Macro

if TYPE_CHECKING:
    from app.window import Window


class CMMacroRow(QFrame):

    def __init__(self, ui: "Window", macro_path: str):
        super().__init__(None)

        self.win = ui
        self.__path = macro_path

        self.main_layout = QHBoxLayout(self)
        self.warn_icon = QFrame(self)
        self.label_layout = QVBoxLayout(self)
        self.label = QLabel()
        self.description = QLabel()
        self.button = QPushButton(self)
        self.create_ui()

        try:
            self.io = CMFile(macro_path)
            self.macro = Macro.from_json(self.io.read())
            self.set_status(True)
        except Exception as e:
            self.set_status(False)
            self.io = None
            self.macro = None

    @property
    def file_path(self):
        return self.__path

    def name(self):
        if self.macro is None:
            return self.file_path
        return self.macro.name

    def getState(self):
        return self.warn_icon.isHidden()

    def create_ui(self):
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.addWidget(self.warn_icon)
        self.warn_icon.setStyleSheet("border-image: url(:/Dialog/dialog/Warn.svg)")
        self.warn_icon.setFixedSize(20, 20)
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.label_layout.addWidget(self.label)
        self.description.setWordWrap(True)
        self.description.setStyleSheet('color: #777777;font: 9pt "Inter"')
        self.description.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignJustify)
        self.label_layout.addWidget(self.description)
        self.main_layout.addLayout(self.label_layout)
        self.button.clicked.connect(self.remove_macro)
        self.main_layout.addWidget(self.button)
        self.main_layout.setSpacing(5)

    def mousePressEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier and event.button() == Qt.LeftButton and self.getState():
            os.system(f"explorer /select,{self.io.path}")
        elif event.button() == Qt.LeftButton:
            if self.getState():
                self.win.choose_saved_macro(self)
            else:
                pth = QFileDialog.getOpenFileName(self, 'Relocate macro file...',
                                                  filter=f"Relocation ({os.path.basename(self.file_path)})")[0]
                if os.path.basename(pth) == os.path.basename(self.file_path):
                    self.win.remove_saved_macro(self)
                    self.win.add_saved_macro(pth, True)

    def remove_macro(self):
        dialog = CMRemoveMacroDialog(self.macro.name)
        if dialog.execResponse().accepted:
            self.win.remove_saved_macro(self)

    def set_status(self, state: bool):
        font = self.label.font()
        font.setStrikeOut(not state)
        self.label.setFont(font)
        self.label.setStyleSheet("" if state else "color: #bbbbbb")
        if state:
            self.warn_icon.hide()
            self.label.setText(utils.crop_string(self.macro.name or "Untitled", 25))
            self.description.setText(utils.crop_string(self.macro.description or "No description provided", 70))
        else:
            self.warn_icon.show()
            self.label.setText(utils.crop_string(os.path.basename(self.file_path), 20))
            self.description.setText("Was not found! Click to relocate!")
