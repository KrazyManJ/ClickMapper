from app.widgets.dialogs.CMBaseDialog import CMBaseDialog


class CMRunInfMacroDialog(CMBaseDialog):
    def __init__(self):
        super().__init__()
        self.BtnReject.hide()
        self.setWarningButton(self.BtnAccept)
        self.DialogText.setText(f"You are trying to execute infinite-loop macro. Are you sure you want to execute it?")
        self.BtnAccept.setText("Execute")
        self.BtnCancel.setText("Cancel")
        self.showIcon(True)