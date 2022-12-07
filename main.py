import sys

from PyQt5.QtWidgets import QApplication

from app.widgets.dialogs.CMAlreadyRunningDialog import CMAlreadyRunningDialog
from app.window import Window
from app.images import resources

if __name__ == '__main__':
    App = QApplication(sys.argv)
    resources.qInitResources()
    if Window.is_already_running():
        CMAlreadyRunningDialog().execResponse()
        sys.exit()
    ui = Window(App)
    ui.show()
    sys.exit(App.exec())
