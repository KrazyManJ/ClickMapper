import ctypes
import json
import os.path

from PyQt5 import uic, QtGui, Qt, QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QWidget, QApplication, QFileDialog
from qframelesswindow import FramelessWindow

import Utils
from .CMTitleBar import CMTitleBar
from .CMMacroRow import CMMacroRow
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

        for saved_path in self.macroListLoad():
            self.macroAdd(saved_path)
        self.titleBar.setMacroTitling(f"Loaded {len(self.macroListLoad())} macros!")
        self.selected_macro_row: CMMacroRow | None = None

        self.MacroList.mouseDoubleClickEvent = self.MacroListDoubleClickEvent

    def shadowEngine(self):
        Utils.apply_shadow(self.MacroListCtr, 80, 2, 4)
        Utils.apply_shadow(self.MacroListTitleLabel, 100)

    def macroChoose(self, macrorow: CMMacroRow):
        if macrorow is self.selected_macro_row:
            return
        if self.selected_macro_row is not None:
            self.selected_macro_row.setStyleSheet("")
        macrorow.setStyleSheet("background-color: #202020")
        self.selected_macro_row = macrorow
        m = Macro.from_macro_file(macrorow.macro_path)
        self.setMacroTitling(m.name, macrorow.macro_path)

    def macroUnselect(self):
        if self.selected_macro_row is None: return
        self.selected_macro_row.setStyleSheet("")
        self.selected_macro_row = None
        self.setIdle()

    def macroDelete(self, macrorow: CMMacroRow):
        macrorow.parent().layout().removeWidget(macrorow)
        if self.selected_macro_row is macrorow:
            self.macroUnselect()
        macrorow.deleteLater()

    def macroAdd(self, file_path):
        pth = os.path.abspath(file_path)
        if pth in self.macroListPath(): return
        if Macro.is_macro_file(file_path):
            m: Macro = Macro.from_macro_file(file_path)
            self.MacroListContent.layout().addWidget(CMMacroRow(self, file_path, m))

    def macroListPath(self):
        return [os.path.abspath(i.macro_path) for i in self.MacroListContent.children() if isinstance(i, CMMacroRow)]

    def macroListSave(self):
        json.dump([os.path.relpath(p) for p in self.macroListPath()],
                  open("saved_macros.json", "w", encoding="utf8", errors="surrogateescape"))

    def macroListLoad(self):
        return set(json.load(open("saved_macros.json", "r", encoding="utf8", errors="surrogateescape")))

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
        self.macroListSave()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        paths = [os.path.abspath(l.toLocalFile()) for l in event.mimeData().urls() if
                 os.path.abspath(l.toLocalFile()) not in self.macroListPath()]
        if len(paths) == 0:
            event.ignore()
            return
        if len([l for l in paths if Macro.is_macro_file(l)]) == 0:
            event.ignore()
            return
        event.accept()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        self.activateWindow()
        for path in a0.mimeData().urls():
            self.macroAdd(path.toLocalFile())

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Qt.Key_Escape:
            self.macroUnselect()

    def MacroListDoubleClickEvent(self, ev):
        for path in QFileDialog.getOpenFileNames(self, 'Open Macro files...', filter="Macro files (*.json)")[0]:
            self.macroAdd(path)
