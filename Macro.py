import abc
import time
import json
from pynput import mouse
from threading import Thread

__MOUSE__ = mouse.Controller()


class MacroEncoder(json.JSONEncoder):

    def default(self, o):
        if type(o) is Macro:
            return {k: v for k, v in o.__dict__.items() if not k.startswith("_")}
        elif isinstance(o, MacroAction):
            return {**o.__dict__, "action_type": type(o).__name__}
        return super().default(o)


class Macro:

    def __init__(self):
        self.actions = []
        self.__is_run__ = False

    def run(self):
        if self.__is_run__: return
        self.__is_run__ = True
        for action in self.actions: action.execute()
        self.__is_run__ = False

    def add_action(self, action):
        self.actions.append(action)

    def run_as_thread(self):
        if self.__is_run__: return
        thr = Thread(target=self.run, name="macro")
        thr.start()
        return thr

    def to_json(self, indent):
        return json.dumps(self, cls=MacroEncoder, indent=4, sort_keys=True)

    @staticmethod
    def from_json(json_data) -> "Macro":

        def hook(data: dict):
            if "action_type" in data:
                return eval(data["action_type"])(**{k: v for k, v in data.items() if k not in ["action_type"]})
            elif list(data.keys()) == [k for k in Macro().__dict__.keys() if not k.startswith("_")]:
                m = Macro(**{k: v for k, v in data.items() if k not in ["actions"]})
                for action in data["actions"]:
                    m.actions.append(action)
                return m

        return json.loads(json_data, object_hook=hook)


class MacroAction(abc.ABC):

    def __init__(self, delay):
        self.delay = delay

    @abc.abstractmethod
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
