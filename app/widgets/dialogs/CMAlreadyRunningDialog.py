from app.widgets.dialogs.CMBaseDialog import CMBaseDialog


class CMAlreadyRunningDialog(CMBaseDialog):
    def __init__(self):
        super().__init__()
        self.BtnAccept.hide()
        self.BtnReject.hide()
        self.DialogText.setText(f"Click Mapper app is already running!")
        self.showIcon(True)