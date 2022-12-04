from app import utils
from app.widgets.dialogs.CMBaseDialog import CMBaseDialog


class CMRemoveMacroDialog(CMBaseDialog):
    def __init__(self, macro_name):
        super().__init__()
        self.BtnCancel.hide()
        self.BtnAccept.setStyleSheet("background-color: #aa3333")
        self.DialogText.setText(f"Are you sure you want to remove macro \"{Utils.crop_string(macro_name, 100)}\"?")
        self.BtnAccept.setText("Remove")
        self.BtnReject.setText("Keep")
        self.showIcon(True)

