from pypresence import Presence
from datetime import datetime

from Tokens import RICH_PRESENCE


class RichPressence:
    RPC: Presence = Presence(RICH_PRESENCE, pipe=0)
    StartTime: int = round(datetime.now().timestamp())

    @classmethod
    def begin(cls):
        cls.RPC.connect()
        cls.setIdle()

    @classmethod
    def setMacroName(cls, name):
        cls.RPC.update(large_image="large_icon", details="Editing Macro", state=name, start=cls.StartTime)

    @classmethod
    def setIdle(cls):
        cls.RPC.update(large_image="large_icon", details="Idling", start=cls.StartTime)

    @classmethod
    def close(cls):
        cls.RPC.close()
