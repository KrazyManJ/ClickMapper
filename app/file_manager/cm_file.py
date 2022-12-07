import os.path
from os import PathLike
import portalocker


class CMFile:
    def __init__(self, path: str | PathLike, def_content: str = None):
        self.__path = path
        if def_content is not None and not os.path.isfile(path): open(path,"a").write(def_content)
        self.__io = None
        self.__io = open(path,"r+",encoding="utf8", errors="surrogateescape")
        if self.__io is not None:
            portalocker.lock(self.__io, portalocker.LockFlags.NON_BLOCKING | portalocker.LockFlags.EXCLUSIVE)

    @property
    def path(self):
        return self.__path

    def read(self):
        self.__io.seek(0)
        return self.__io.read()

    def write(self, text: str):
        self.__io.seek(0)
        self.__io.write(text)
        self.__io.truncate()

    def unlock(self):
        portalocker.unlock(self.__io)

    def __del__(self):
        if self.__io is not None:
            self.unlock()


