from dataclasses import dataclass
from typing import TypedDict
import typing


class Instructions(TypedDict):
    var: dict
    jobs: dict
    meta: dict


@dataclass
class ZutoCmd:
    name: str
    func: typing.Callable
    scope: str = None
    prop: bool = False
    cached: bool = False
    resolve_strings: bool = True

    def __post_init__(self):
        self._cached = None

    def invoke(self, *args, **kwargs):
        if self.cached and self._cached:
            return self._cached
        elif self.cached:
            self._cached = self.func(*args, **kwargs)
            return self._cached
        else:
            return self.func(*args, **kwargs)
