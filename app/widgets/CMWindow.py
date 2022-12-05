import ctypes
import json
import os.path
from os.path import abspath

from PyQt5 import uic, QtGui, Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QWidget, QFileDialog, QLineEdit
from qframelesswindow import FramelessWindow

from .. import utils, pather
from .CMTitleBar import CMTitleBar
from .CMMacroRow import CMMacroRow
from app.macro.Macro import Macro
from app.rich_presence import RichPressence
from .dialogs.CMRunInfMacroDialog import CMRunInfMacroDialog
from ..macro.macro_runner import MacroRunner


class CMWindow(FramelessWindow):
    MacroListCtr: QFrame
    MacroListTitle: QFrame
    MacroListTitleLabel: QLabel
    MacroList: QScrollArea
    MacroListContent: QWidget
    MacroListFilterInput: QLineEdit

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.threadpool = QThreadPool()
        self.selected_macro_row = None

        uic.loadUi(pather.ui_design_file("design.ui"), self)
        self.shadowEngine()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.ClickMapper.1.0.0")
        self.setWindowIcon(QIcon(":/Favicon/favicon/icon.svg"))
        self.setTitleBar(CMTitleBar(self))  # type: ignore
        utils.center_widget(self.app, self)
        self.titleBar.raise_()

        self.MacroListFilterInput.addAction(
            QIcon(":/TitleBar/title_bar/ClsBtn.svg"),
            QLineEdit.ActionPosition.TrailingPosition
        ).triggered.connect(self.MacroListFilterInput.clear)


        RichPressence.begin()

        for saved_path in self.load_saved_macros(): self.add_saved_macro(saved_path)
        self.titleBar.setMacroTitling(f"Loaded {len(self.load_saved_macros())} macros!")

        self.MacroList.mouseDoubleClickEvent = self.MacroListDoubleClickEvent
        self.MacroListFilterInput.textChanged.connect(self.filter_saved_macro)

    def shadowEngine(self):
        utils.apply_shadow(self.MacroListCtr, 80, 2, 4)
        utils.apply_shadow(self.MacroListTitleLabel, 100)
        utils.apply_shadow(self.MacroListFilterInput, 40, x=2)

    def setMacroTitling(self, title: str, path: str):
        self.setWindowTitle(f"Click Mapper - {title}")
        self.titleBar.setMacroTitling(f"{title} ({path})")
        RichPressence.setMacroName(title)

    def setIdle(self):
        self.setWindowTitle(f"Click Mapper")
        self.titleBar.setMacroTitling("")
        RichPressence.setIdle()

    # =======================================================================================
    #   SAVED MACRO SECTION
    # =======================================================================================

    def choose_saved_macro(self, macrorow):
        if macrorow is self.selected_macro_row:
            return
        if self.selected_macro_row is not None:
            self.selected_macro_row.setStyleSheet("")
        macrorow.setStyleSheet("background-color: #202020")
        self.selected_macro_row = macrorow
        m = Macro.from_macro_file(macrorow.macro_path)
        self.setMacroTitling(m.name, macrorow.macro_path)

    def unselect_saved_macro(self):
        if self.selected_macro_row is None: return
        self.selected_macro_row.setStyleSheet("")
        self.selected_macro_row = None
        self.setIdle()

    def remove_saved_macro(self, macrorow):
        macrorow.parent().layout().removeWidget(macrorow)
        if self.selected_macro_row is macrorow:
            self.unselect_saved_macro()
        macrorow.deleteLater()
        self.sort_macro_rows()

    def add_saved_macro(self, file_path):
        pth = abspath(file_path)
        if pth in self.macro_list_paths(): return
        if Macro.is_macro_file(file_path):
            m: Macro = Macro.from_macro_file(file_path)
            self.MacroListContent.layout().addWidget(CMMacroRow(self, file_path, m))
        self.sort_macro_rows()

    def filter_saved_macro(self):
        t = self.MacroListFilterInput.text().lower()
        for row in self.saved_macros_rows():
            if (row.macro.name or "").lower().__contains__(t) or (row.macro.description or "").lower().__contains__(t):
                row.show()
            else:
                row.hide()

    def macro_list_paths(self):
        return [abspath(i.macro_path) for i in self.MacroListContent.children() if isinstance(i, CMMacroRow)]

    def save_saved_macros(self):
        json.dump([os.path.relpath(p) for p in self.macro_list_paths()],
                  open(pather.SAVED_MACRO_PATH, "w", encoding="utf8", errors="surrogateescape"))

    def load_saved_macros(self):
        return set(json.load(open(pather.SAVED_MACRO_PATH, "r", encoding="utf8", errors="surrogateescape")))

    def saved_macros_rows(self):
        return [i for i in self.MacroListContent.children() if isinstance(i, CMMacroRow)]

    def sort_macro_rows(self):
        for i, row in enumerate(utils.alphanumeric_sort(self.saved_macros_rows(), key=lambda x: x.macro.name)):
            self.MacroListContent.layout().insertWidget(i, row)

    def run_macro_from_row(self, macrorow):
        if macrorow.macro.is_infinite():
            if not CMRunInfMacroDialog().execResponse().accepted:
                return
        self.threadpool.start(MacroRunner(macrorow.macro))

    # =======================================================================================
    #   EVENTS
    # =======================================================================================

    def closeEvent(self, event: QCloseEvent) -> None:
        RichPressence.close()
        self.save_saved_macros()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        paths = [abspath(l.toLocalFile()) for l in event.mimeData().urls() if
                 abspath(l.toLocalFile()) not in self.macro_list_paths()]
        if len(paths) == 0:
            event.ignore()
            return
        if len([l for l in paths if Macro.is_macro_file(l)]) == 0:
            event.ignore()
            return
        event.accept()

    def dropEvent(self, event) -> None:
        self.activateWindow()
        for path in event.mimeData().urls():
            self.add_saved_macro(path.toLocalFile())

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Qt.Key_Escape:
            self.unselect_saved_macro()

    def MacroListDoubleClickEvent(self, ev):
        for path in QFileDialog.getOpenFileNames(self, 'Open Macro files...', filter="Macro files (*.json)")[0]:
            self.add_saved_macro(path)
