from pypresence import Presence
from datetime import datetime

from Tokens import RICH_PRESENCE


class RichPressence:
    RPC: None | Presence

    @classmethod
    def begin(cls):
        try:
            cls.RPC: Presence = Presence(RICH_PRESENCE, pipe=0)
            cls.StartTime: int = round(datetime.now().timestamp())
            cls.RPC.connect()
            cls.setIdle()
        except:
            pass

    @classmethod
    def setMacroName(cls, name):
        try:
            cls.RPC.update(large_image="large_icon", details="Editing Macro", state=name, start=cls.StartTime)
        except:
            pass

    @classmethod
    def setIdle(cls):
        try:
            cls.RPC.update(large_image="large_icon", details="Idling", start=cls.StartTime)
        except:
            pass

    @classmethod
    def close(cls):
        try:
            cls.RPC.close()
        except:
            pass
