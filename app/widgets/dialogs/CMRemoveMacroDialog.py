from app import utils
from app.widgets.dialogs.CMBaseDialog import CMBaseDialog


class CMRemoveMacroDialog(CMBaseDialog):
    def __init__(self, macro_name):
        super().__init__()
        self.BtnCancel.hide()
        self.setWarningButton(self.BtnAccept)
        self.DialogText.setText(f"Are you sure you want to remove macro \"{utils.crop_string(macro_name, 100)}\"?")
        self.BtnAccept.setText("Remove")
        self.BtnReject.setText("Keep")
        self.showIcon(True)