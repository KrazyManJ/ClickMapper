import sys

from PyQt5.QtWidgets import QApplication

from app.images import resources
from app.widgets.CMWindow import CMWindow

if __name__ == '__main__':
    App = QApplication(sys.argv)
    ui = CMWindow(App)
    ui.show()
    resources.qInitResources()
    sys.exit(App.exec())
