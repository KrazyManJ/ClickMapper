from PyQt5.QtCore import QRunnable, pyqtSlot


class MacroRunner(QRunnable):
    def __init__(self, macro) -> None:
        super().__init__()
        self.macro = macro

    @pyqtSlot()
    def run(self):
        self.macro.run()
