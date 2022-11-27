import abc
import time
from pynput import mouse
from threading import Thread

# Add pixel art to figma

__MOUSE__ = mouse.Controller()


class Macro:

    def __init__(self):
        self.__actions__ = []
        self.__is_run__ = False

    def run(self):
        if self.__is_run__: return
        self.__is_run__ = True
        for action in self.__actions__: action.execute()
        self.__is_run__ = False

    def add_action(self, action):
        self.__actions__.append(action)

    def __getitem__(self, item):
        return self.__actions__[item]

    def __delitem__(self, key):
        del self.__actions__[key]

    def run_as_thread(self):
        if self.__is_run__: return
        thr = Thread(target=self.run, name="macro")
        thr.start()
        return thr


class MouseAction(abc.ABC):

    def __init__(self, delay):
        self.delay = delay

    @abc.abstractmethod
    def execute(self):
        time.sleep(self.delay / 1000)


class MouseMove(MouseAction):

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


class MouseClick(MouseAction):

    def __init__(self, button, click_type, delay):
        super().__init__(delay)
        self.click_type = click_type
        self.button = button

    def execute(self):
        super().execute()
        MAP = {"press": __MOUSE__.press, "release": __MOUSE__.release, "click": __MOUSE__.click}
        if self.click_type in MAP.keys() and mouse.Button[self.button] is not None:
            MAP[self.click_type](mouse.Button[self.button])


class MouseScroll(MouseAction):

    def __init__(self, dx, dy, delay):
        super().__init__(delay)
        self.dx = dx
        self.dy = dy

    def execute(self):
        super().execute()
        __MOUSE__.scroll(self.dx, self.dy)