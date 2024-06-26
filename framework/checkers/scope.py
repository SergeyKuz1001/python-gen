from .abstract import AbstractChecker

from ..trace_language import NotIn

from abc import ABC
from libcst import CSTNode, Name, IndentedBlock, FunctionDef
from typing import Optional, Callable, Any, Iterator


class ScopeChecker(AbstractChecker, ABC):

    def start_generation(self, generator: "Generator") -> None:
        self._scopes: list[dict[str, Any]] = []

    def _begin(self) -> None:
        self._scopes.append(dict())

    def _end(self) -> None:
        self._scopes.pop()

    @property
    def last(self) -> dict[str, Any]:
        return self._scopes[-1]

    def add(self, name: str, info: Any) -> None:
        self.last[name] = info

    def update(self, name: str, func: Callable[Optional[Any], Any]) -> None:
        for i, scope in reversed(list(enumerate(self._scopes))):
            for name_, info in scope.items():
                if name_ == name:
                    self._scopes[i][name] = func(info)
                    return

    def revisit_mid_node(
        self,
        mid_node: CSTNode,
        new_node: Optional[CSTNode],
        generator: "Generator",
    ) -> None:
        if generator.on_trace("function_def", "parameters"):
            self._begin()
        elif generator.on_trace("module"):
            self._begin()
        elif generator.on_trace(
            NotIn(("function_def", "module")), "indented_block"
        ):
            self._begin()

    def releave_mid_node(
        self,
        mid_node: CSTNode,
        new_node: Optional[CSTNode],
        generator: "Generator",
    ) -> None:
        if generator.on_trace("indented_block"):
            self._end()

    class _InfoObject:
        def __imod__(
            self, func: Callable[Optional[Any], Any]
        ) -> "ScopeChecker._InfoObject":
            self.func = func
            return self

    def __getitem__(self, name: str) -> Any:
        return ScopeChecker._InfoObject()

    def __setitem__(self, name: str, info: Any) -> None:
        if type(info) == ScopeChecker._InfoObject:
            self.update(name, info.func)
        else:
            self.add(name, info)

    def __iter__(self) -> "ScopeChecker._Iterator":
        return ScopeChecker._Iterator(self._scopes)

    class _Iterator:
        def __init__(self, scopes: list[dict[str, Any]]):
            self.iter1: Iterator[dict[str, Any]] = iter(scopes)
            self.iter2: Optional[Iterator[tuple[str, Any]]] = None

        def __iter__(self) -> "ScopeChecker._Iterator":
            return self

        def __next__(self) -> tuple[str, Any]:
            while True:
                if self.iter2 is not None:
                    try:
                        return next(self.iter2)
                    except StopIteration:
                        self.iter2 = None
                else:
                    self.iter2 = iter(next(self.iter1).items())
