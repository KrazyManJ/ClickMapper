import sys

from PyQt5.QtWidgets import QApplication

from app.window import CMWindow

if __name__ == '__main__':
    App = QApplication(sys.argv)
    ui = CMWindow(App)
    ui.show()
    sys.exit(App.exec())
