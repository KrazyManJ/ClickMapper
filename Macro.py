import os.path
import time
import json
from datetime import datetime

import jsonschema
from pynput import mouse
from threading import Thread

__MOUSE__ = mouse.Controller()

INFINITE = -1

class MacroEncoder(json.JSONEncoder):

    def default(self, o):
        if type(o) is Macro:
            return {k: v for k, v in o.__dict__.items() if not k.startswith("_")}
        elif isinstance(o, MacroAction):
            return {"action_type": type(o).__name__, **o.__dict__}
        return super().default(o)


class Macro:

    def __init__(self, name=None, description=None, author=None, number_of_executions=1, executions_delay=0):

        self.name = name
        self.description = description
        self.author = author
        self.number_of_executions = number_of_executions
        self.executions_delay = executions_delay

        self.actions = []

        self.__is_run__ = False
        self.__delay__: None | datetime = None
        self.__term__ = False

    def run(self):
        if self.__is_run__: return
        self.__is_run__ = True

        if self.number_of_executions <= 0:
            while True:
                for action in self.actions:
                    if self.__term__: break
                    action.execute()
                    if self.__term__: break
                time.sleep(self.executions_delay / 1000)
                if self.__term__: break
        else:
            for i in range(self.number_of_executions):
                for action in self.actions:
                    if self.__term__: break
                    action.execute()
                    if self.__term__: break
                time.sleep(self.executions_delay / 1000)
                if self.__term__: break
        self.__is_run__ = False

    def run_as_thread(self):
        if self.__is_run__: return
        thr = Thread(target=self.run, name="macro")
        thr.start()
        return thr

    def terminate(self):
        if not self.__is_run__: return
        self.__term__ = True

    def to_json(self, indent=None):
        return json.dumps(self, cls=MacroEncoder, indent=indent)

    @staticmethod
    def is_macro_json(json_data):
        try:
            jsonschema.validate(
                instance=json.loads(json_data),
                schema=json.load(open(os.path.join(os.path.dirname(__file__),"macro_schema.json"), "r"))
            )
        except Exception:
            return False
        return True

    @staticmethod
    def from_json(json_data):
        if not Macro.is_macro_json(json_data): return None

        def hook(data: dict):
            if "action_type" in data:
                return eval(data["action_type"])(**{k: v for k, v in data.items() if k not in ["action_type"]})
            elif set(data.keys()) == {k for k in Macro().__dict__.keys() if not k.startswith("_")}:
                m = Macro(**{k: v for k, v in data.items() if k not in ["actions"]})
                for action in data["actions"]:
                    m.actions.append(action)
                return m

        return json.loads(json_data, object_hook=hook)

    def __delta__(self):
        return round((datetime.now() - self.__delay__).total_seconds() * 1000, 2)

    def start_recording(self):
        if self.is_recording(): return

        def scrl(x, y, dx, dy):
            if not self.is_recording(): return False
            self.actions.append(MouseMove("a", x, y, self.__delta__()))
            self.actions.append(MouseScroll(dx, dy, 0))
            self.__delay__ = datetime.now()

        def clk(x, y, button, state):
            if not self.is_recording(): return False
            self.actions.append(MouseMove("a", x, y, self.__delta__()))
            self.actions.append(MouseClick(button.name, "press" if state else "release", 0))
            self.__delay__ = datetime.now()

        self.__delay__ = datetime.now()
        mouse.Listener(on_scroll=scrl, on_click=clk).start()

    def stop_recording(self):
        if not self.is_recording(): return
        self.executions_delay = self.__delta__()
        self.__delay__ = None

    def is_recording(self):
        return self.__delay__ is not None

    def execution_time(self):
        return sum([a.delay for a in self.actions]) + self.executions_delay

    def total_execution_time(self):
        return self.execution_time() * self.number_of_executions


class MacroAction:

    def __init__(self, delay):
        self.delay = delay

    def execute(self):
        time.sleep(self.delay / 1000)


class MouseMove(MacroAction):

    def __init__(self, position, x, y, delay):
        super().__init__(delay)
        self.position = position
        self.x = x
        self.y = y

    def execute(self):
        super().execute()
        if self.position == "r":
            __MOUSE__.move(self.x or 0, self.y or 0)
        elif self.position == "a":
            __MOUSE__.position = self.x or __MOUSE__.position[0], self.y or __MOUSE__.position[1]


class MouseClick(MacroAction):

    def __init__(self, button, click_type, delay):
        super().__init__(delay)
        self.click_type = click_type
        self.button = button

    def execute(self):
        super().execute()
        MAP = {"press": __MOUSE__.press, "release": __MOUSE__.release, "click": __MOUSE__.click}
        if self.click_type in MAP.keys() and mouse.Button[self.button] is not None:
            MAP[self.click_type](mouse.Button[self.button])


class MouseScroll(MacroAction):

    def __init__(self, dx, dy, delay):
        super().__init__(delay)
        self.dx = dx
        self.dy = dy

    def execute(self):
        super().execute()
        __MOUSE__.scroll(self.dx, self.dy)
