import ctypes
import json
from os.path import abspath, relpath

from PyQt5 import uic, QtGui, Qt  # type: ignore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QWidget, QFileDialog, QLineEdit
from qframelesswindow import FramelessWindow

from app import utils, pather
from app.file_manager.cm_file import CMFile
from app.images import resources
from app.widgets.CMTitleBar import CMTitleBar
from app.widgets.CMMacroRow import CMMacroRow
from app.macro.Macro import Macro
from app.rich_presence import RichPressence
from app.widgets.dialogs.CMRunInfMacroDialog import CMRunInfMacroDialog
from app.macro.macro_runner import MacroRunner


class CMWindow(FramelessWindow):

    MACRO_LIST_FILE = CMFile(pather.SAVED_MACRO_PATH, "[]")

    # =======================================================================================
    #   WIDGET LIST
    # =======================================================================================

    MacroListCtr: QFrame
    MacroListTitle: QFrame
    MacroListTitleLabel: QLabel
    MacroList: QScrollArea
    MacroListContent: QWidget
    MacroListFilterInput: QLineEdit

    # =======================================================================================
    #   INITIALIZATION
    # =======================================================================================

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.threadpool = QThreadPool()
        self.selected_macro_row = None

        resources.qInitResources()
        QtGui.QFontDatabase.addApplicationFont("fonts/Inter.ttf")

        uic.loadUi(pather.ui_design_file("design.ui"), self)
        self.shadowEngine()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.ClickMapper.1.0.0")
        self.setWindowIcon(QIcon(":/Favicon/favicon/icon.svg"))
        self.setTitleBar(CMTitleBar(self))  # type: ignore
        utils.center_widget(self.app, self)

        self.MacroListFilterInput.addAction(QIcon(":/TitleBar/title_bar/ClsBtn.svg"),  # type: ignore
                                            QLineEdit.ActionPosition.TrailingPosition).triggered.connect(
            self.MacroListFilterInput.clear)

        RichPressence.begin()

        for saved_path in self.load_saved_macros(): self.add_saved_macro(saved_path)
        self.titleBar.setMacroTitling(f"Loaded {len(self.load_saved_macros())} macros!")

        self.MacroList.mouseDoubleClickEvent = self.MacroListDoubleClickEvent
        self.MacroListFilterInput.textChanged.connect(self.filter_saved_macro)  # type: ignore

    def shadowEngine(self):
        utils.apply_shadow(self.MacroListCtr, 80, 2, 4)
        utils.apply_shadow(self.MacroListTitleLabel, 100)
        utils.apply_shadow(self.MacroListFilterInput, 40, x=2)

    def setMacroTitling(self, title: str, path: str):
        self.setWindowTitle(f"Click Mapper - {title}")
        self.titleBar.setMacroTitling(f"{title} ({abspath(path)})")
        RichPressence.setMacroName(title)

    def setIdle(self):
        self.setWindowTitle(f"Click Mapper")
        self.titleBar.setMacroTitling("")
        RichPressence.setIdle()

    # =======================================================================================
    #   SAVED MACRO SECTION
    # =======================================================================================

    def choose_saved_macro(self, macrorow: CMMacroRow):
        if macrorow is self.selected_macro_row:
            return
        if self.selected_macro_row is not None:
            self.selected_macro_row.setStyleSheet("")
        macrorow.setStyleSheet("background-color: #202020")
        self.selected_macro_row = macrorow
        self.setMacroTitling(macrorow.macro.name, macrorow.file_path)

    def unselect_saved_macro(self):
        if self.selected_macro_row is None: return
        self.selected_macro_row.setStyleSheet("")
        self.selected_macro_row = None
        self.setIdle()

    def remove_saved_macro(self, macrorow: CMMacroRow):
        macrorow.parent().layout().removeWidget(macrorow)
        if self.selected_macro_row is macrorow:
            self.unselect_saved_macro()
        if macrorow.getState():
            macrorow.io.unlock()
        macrorow.deleteLater()
        self.sort_saved_macro_rows()

    def add_saved_macro(self, file_path, replace=False):
        pth = abspath(file_path)
        if pth in self.macro_list_paths() and not replace: return
        self.MacroListContent.layout().addWidget(CMMacroRow(self, file_path))
        self.sort_saved_macro_rows()

    def user_add_saved_macro(self, file_path):
        if Macro.is_macro_file(file_path):
            self.add_saved_macro(file_path)

    def filter_saved_macro(self):
        t = self.MacroListFilterInput.text().lower()
        for row in self.saved_macros_rows():
            if t in (row.macro.name or "").lower() or t in (row.macro.description or "").lower():
                row.show()
            else:
                row.hide()

    def macro_list_paths(self):
        return [abspath(i.file_path) for i in self.saved_macros_rows()]

    def save_saved_macros(self):
        self.MACRO_LIST_FILE.write(json.dumps([relpath(p) for p in self.macro_list_paths()]))

    def load_saved_macros(self):
        return set(json.loads(self.MACRO_LIST_FILE.read()))

    def saved_macros_rows(self):
        return [i for i in self.MacroListContent.children() if isinstance(i, CMMacroRow)]

    def sort_saved_macro_rows(self):
        for i, row in enumerate(utils.alphanumeric_sort(self.saved_macros_rows(), key=lambda x: x.name())):
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
            self.user_add_saved_macro(path.toLocalFile())

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Qt.Key_Escape:
            self.unselect_saved_macro()

    def MacroListDoubleClickEvent(self, ev):
        for path in QFileDialog.getOpenFileNames(self, 'Open Macro files...', filter="Macro files (*.json)")[0]:
            self.user_add_saved_macro(path)
