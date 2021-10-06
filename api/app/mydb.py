import abc
from typing import Dict, Optional, Union
from typing import Any
try:
    import ujson as json
except ImportError:
    import json


class DB(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def lookup(self, identifier: str) -> Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def exist(self, identifier: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, identifier: str, data: Union[str, Dict[str, Any]]) -> Optional[str]:
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class JsonDB(DB):
    __slots__ = ('_path', '_has_writes')

    def __init__(self, path: str) -> None:
        self._path: str = path
        self._has_writes: bool = False
        with open(path) as f:
            self._db: dict = json.load(f)

    def exist(self, identifier: str) -> bool:
        return identifier in self._db

    def lookup(self, identifier: str, default: Any = None) -> Optional[str]:
        return self._db.get(identifier, default)

    def set(self, identifier: str, data: Union[str, Dict[str, Any]]) -> Optional[str]:
        self._db[identifier] = data
        self._has_writes = True

    def __exit__(self, exc_type, exc_value, traceback):
        # dump db when exit the context and not exception occur and at least one set operation happer
        if exc_type is None and self._has_writes:
            with open(self._path, 'w') as f:
                json.dump(self._db, f)
