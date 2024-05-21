from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union, Callable

Node = Union[type, str]


class AbstractFilter(ABC):
    @abstractmethod
    def match(self, node: Node) -> bool: ...


class GlobalFilter(AbstractFilter, ABC):
    pass


class LocalFilter(AbstractFilter, ABC):
    @abstractmethod
    def exhaust(self) -> bool: ...


class SpotFilter(LocalFilter, ABC):
    def exhaust(self) -> bool:
        return True


@dataclass(frozen=True)
class AllNodes(GlobalFilter):
    def match(self, node: Node) -> bool:
        return True


@dataclass(frozen=True)
class OnlyGenNodes(GlobalFilter):
    def match(self, node: Node) -> bool:
        return type(node) == str


@dataclass(frozen=True)
class SearchThroughMany(LocalFilter):
    target: Union[Node, SpotFilter]
    filter_: Union[Node, SpotFilter]

    def match(self, node: Node) -> bool:
        object.__setattr__(self, "_is_exhaust", _match(self.target, node))
        return _match(self.filter_, node) or _match(self.target, node)

    def exhaust(self) -> bool:
        return self._is_exhaust


@dataclass(frozen=True)
class In(SpotFilter):
    nodes: list[Node]

    def match(self, node: Node) -> bool:
        return node in self.nodes


@dataclass(frozen=True)
class NotIn(SpotFilter):
    nodes: list[Node]

    def match(self, node: Node) -> bool:
        return node not in self.nodes


@dataclass(frozen=True)
class Any(SpotFilter):
    def match(self, node: Node) -> bool:
        return True


def _match(self: Union[Node, LocalFilter], node: Node) -> bool:
    if isinstance(self, LocalFilter):
        return self.match(node)
    else:
        return self == node


def _exhaust(self: Union[Node, LocalFilter]) -> bool:
    if isinstance(self, LocalFilter):
        return self.exhaust()
    else:
        return True


def is_matched(
    trace: list[Node],
    global_filter: GlobalFilter,
    local_filters: list[Union[Node, LocalFilter]],
) -> bool:
    if (
        len(trace) == 0
        or len(local_filters) == 0
        or not _match(local_filters[-1], trace[-1])
    ):
        return False
    i, j = -1, -1
    while -i <= len(local_filters):
        if -j > len(trace):
            return False
        elif not global_filter.match(trace[j]):
            j -= 1
        elif _match(local_filters[i], trace[j]):
            i -= _exhaust(local_filters[i])
            j -= 1
        else:
            return False
    return True
