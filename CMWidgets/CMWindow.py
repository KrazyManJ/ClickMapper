import ctypes
import json
import os.path

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QWidget, QApplication, QVBoxLayout
from qframelesswindow import FramelessWindow

import Utils
from .CMMacroRow import CMMacroRow
from .CMTitleBar import CMTitleBar
from Macro import Macro
from RichPresence import RichPressence

# class MacroRunner(QRunnable):
#
#     @pyqtSlot()
#     def run(self):
#         Macro.from_json(open("default_macros/my_test_macro.json","r").read()).run()

class CMWindow(FramelessWindow):

    MacroListCtr: QFrame
    MacroListTitle: QFrame
    MacroListTitleLabel: QLabel
    MacroList: QScrollArea
    MacroListContent: QWidget

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.threadpool = QThreadPool()

        # UI LOADING, ICON, TITLEBAR, SHADOWENGINE

        uic.loadUi("ui/design.ui", self)
        self.shadowEngine()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.ClickMapper.1.0.0")
        self.setWindowIcon(QIcon(":/favicon/icon.svg"))
        self.setTitleBar(CMTitleBar(self))  # type: ignore
        self.titleBar.raise_()

        # CENTER

        frameGm = self.frameGeometry()
        frameGm.moveCenter(self.app.desktop().screenGeometry(
            self.app.desktop().screenNumber(self.app.desktop().cursor().pos())).center())
        self.move(frameGm.topLeft())

        # RICH PRESENCE

        RichPressence.begin()

        for saved_path in set(json.load(open("saved_macros.json","r"))):
            self.macroAdd(os.path.abspath(saved_path))
        self.selected_macro_row:CMMacroRow | None = None

    def shadowEngine(self):
        Utils.apply_shadow(self.MacroListCtr, 80, 2, 4)
        Utils.apply_shadow(self.MacroListTitleLabel, 100)



    def macroChoose(self, macrorow: CMMacroRow):
        if macrorow is self.selected_macro_row: return
        if self.selected_macro_row is not None: self.selected_macro_row.setStyleSheet("")
        macrorow.setStyleSheet("background-color: #202020")
        self.selected_macro_row = macrorow
        m = Macro.from_json(open(macrorow.macro_path,"r",encoding="utf8",errors="surrogateescape").read())
        self.setMacroTitling(m.name,macrorow.macro_path)

    def macroDelete(self, macrorow: CMMacroRow):
        macrorow.parent().layout().removeWidget(macrorow)
        if self.selected_macro_row is macrorow:
            self.selected_macro_row.setStyleSheet("")
            self.selected_macro_row = None
            self.setIdle()
        macrorow.deleteLater()

    def macroAdd(self, file_path):
        jsondata = open(file_path, "r",encoding="utf8",errors="surrogateescape").read()
        if Macro.is_macro_json(jsondata):
            m: Macro = Macro.from_json(jsondata)
            self.MacroListContent.layout().addWidget(
                CMMacroRow(self, file_path, title=m.name or "untitled", author=m.author or "unknown")
            )

    def macroListPath(self):
        return [i.macro_path for i in self.MacroListContent.children() if isinstance(i,CMMacroRow)]

    def setMacroTitling(self, title: str, path: str):
        self.setWindowTitle(f"Click Mapper - {title}")
        self.titleBar.setMacroTitling(f"{title} ({path})")
        RichPressence.setMacroName(title)

    def setIdle(self):
        self.setWindowTitle(f"Click Mapper")
        self.titleBar.setMacroTitling("")
        RichPressence.setIdle()

    def closeEvent(self, event: QCloseEvent) -> None:
        RichPressence.close()
        json.dump(self.macroListPath(),open("saved_macros.json","w",encoding="utf8",errors="surrogateescape"))

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls: event.accept()
        else: event.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        self.activateWindow()
        INCL_PATHS = [i.macro_path for i in self.MacroListContent.children() if isinstance(i,CMMacroRow)]
        for path in a0.mimeData().urls():
            pth = os.path.abspath(path.toLocalFile())
            if pth not in INCL_PATHS:
                self.macroAdd(pth)
