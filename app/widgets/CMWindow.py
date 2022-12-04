import ctypes
import json
import os.path
from os.path import abspath,dirname,pardir,join as pathjoin

from PyQt5 import uic, QtGui, Qt
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QWidget, QApplication, QFileDialog
from qframelesswindow import FramelessWindow

from .. import utils
from .CMTitleBar import CMTitleBar
from .CMMacroRow import CMMacroRow
from app.macro.Macro import Macro
from app.rich_presence import RichPressence
from .dialogs.CMRunInfMacroDialog import CMRunInfMacroDialog


class MacroRunner(QRunnable):
    def __init__(self,macro) -> None:
        super().__init__()
        self.macro = macro

    @pyqtSlot()
    def run(self):
        self.macro.run()


class CMWindow(FramelessWindow):

    __SAVED_MACROS_PATH__ = pathjoin(dirname(__file__),pardir,"saved_macros.json")


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

        uic.loadUi(os.path.join(os.path.dirname(__file__), os.pardir,"ui","design.ui"), self)
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
        utils.apply_shadow(self.MacroListCtr, 80, 2, 4)
        utils.apply_shadow(self.MacroListTitleLabel, 100)

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
        pth = abspath(file_path)
        if pth in self.macroListPath(): return
        if Macro.is_macro_file(file_path):
            m: Macro = Macro.from_macro_file(file_path)
            self.MacroListContent.layout().addWidget(CMMacroRow(self, file_path, m))

    def macroListPath(self):
        return [abspath(i.macro_path) for i in self.MacroListContent.children() if isinstance(i, CMMacroRow)]

    def macroListSave(self):
        json.dump([os.path.relpath(p) for p in self.macroListPath()],
                  open(self.__SAVED_MACROS_PATH__, "w", encoding="utf8", errors="surrogateescape"))

    def macroListLoad(self):
        return set(json.load(open(self.__SAVED_MACROS_PATH__, "r", encoding="utf8", errors="surrogateescape")))

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
        paths = [abspath(l.toLocalFile()) for l in event.mimeData().urls() if
                 abspath(l.toLocalFile()) not in self.macroListPath()]
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

    def macroRun(self, macrorow: CMMacroRow):
        if macrorow.macro.is_infinite():
            if not CMRunInfMacroDialog().execResponse().accepted:
                return
        self.threadpool.start(MacroRunner(macrorow.macro))
