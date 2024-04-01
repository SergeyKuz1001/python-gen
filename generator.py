from gen_node import GenNode
from choose import Choose
from config import Config
from abstract_checker import AbstractChecker
from failures import AllowableFailure, UnexpectedFailure

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import FunctionType
from typing import Optional, Union, Callable
from libcst import CSTTransformer, CSTNode, CSTNodeT


class TL:
    Node = Union[type, str]

    class Filter(ABC):
        @abstractmethod
        def match(self, node: "TL.Node") -> bool: ...

    class GlobalFilter(Filter, ABC):
        pass

    class LocalFilter(Filter, ABC):
        @abstractmethod
        def exhaust(self) -> bool: ...

    class SpotFilter(LocalFilter, ABC):
        def exhaust(self) -> bool:
            return True

    @dataclass(frozen=True)
    class AllNodes(GlobalFilter):
        def match(self, node: "TL.Node") -> bool:
            return True

    @dataclass(frozen=True)
    class OnlyGenNodes(GlobalFilter):
        def match(self, node: "TL.Node") -> bool:
            return type(node) == str

    @dataclass(frozen=True)
    class SearchThroughMany(LocalFilter):
        target: Union["TL.Node", "TL.SpotFilter"]
        filter_: Union["TL.Node", "TL.SpotFilter"]

        def match(self, node: "TL.Node") -> bool:
            object.__setattr__(self, "_is_exhaust", TL._match(self.target, node))
            return TL._match(self.filter_, node) or TL._match(self.target, node)

        def exhaust(self) -> bool:
            return self._is_exhaust

    @dataclass(frozen=True)
    class In(SpotFilter):
        nodes: list["TL.Node"]

        def match(self, node: "TL.Node") -> bool:
            return node in self.nodes

    @dataclass(frozen=True)
    class NotIn(SpotFilter):
        nodes: list["TL.Node"]

        def match(self, node: "TL.Node") -> bool:
            return node not in self.nodes

    @dataclass(frozen=True)
    class Any(SpotFilter):
        def match(self, node: "TL.Node") -> bool:
            return True

    @staticmethod
    def _match(self: Union["TL.Node", "TL.LocalFilter"], node: "TL.Node") -> bool:
        if isinstance(self, TL.LocalFilter):
            return self.match(node)
        else:
            return self == node

    @staticmethod
    def _exhaust(self: Union["TL.Node", "TL.LocalFilter"]) -> bool:
        if isinstance(self, TL.LocalFilter):
            return self.exhaust()
        else:
            return True

    @staticmethod
    def match(
        trace: list["TL.Node"],
        global_filter: "TL.GlobalFilter",
        local_filters: list[Union["TL.Node", "TL.LocalFilter"]],
    ) -> bool:
        if (
            len(trace) == 0
            or len(local_filters) == 0
            or not TL._match(local_filters[-1], trace[-1])
        ):
            return False
        i, j = -1, -1
        while -i <= len(local_filters):
            if -j > len(trace):
                return False
            elif not global_filter.match(trace[j]):
                j -= 1
            elif TL._match(local_filters[i], trace[j]):
                i -= TL._exhaust(local_filters[i])
                j -= 1
            else:
                return False
        return True


@dataclass(frozen=True)
class Generator(CSTTransformer):
    choose: Choose
    config: Config
    checkers: list[AbstractChecker]

    def __init__(self, seed: int, config: Config, checkers: list[AbstractChecker]):
        object.__setattr__(self, "choose", Choose(seed))
        object.__setattr__(self, "config", config)
        object.__setattr__(self, "checkers", checkers)
        object.__setattr__(self, "_trace", [])
        object.__setattr__(self, "_trans_list", [])
        self.on_start_generation()

    def find_checker(self, checker_type: type) -> Optional[AbstractChecker]:
        checkers = list(
            filter(lambda checker: type(checker) == checker_type, self.checkers)
        )
        if len(checkers) == 0:
            return None
        elif len(checkers) == 1:
            return checkers[0]
        else:
            raise UnexpectedFailure("Many checkers of same type were found")

    def on_trace(self, *local_filters) -> bool:
        if isinstance(local_filters[0], TL.GlobalFilter):
            global_filter, local_filters = local_filters[0], local_filters[1:]
        else:
            global_filter = (
                TL.OnlyGenNodes()
                if all(
                    map(
                        lambda lf: type(lf) == str or isinstance(lf, TL.Filter),
                        local_filters,
                    )
                )
                else TL.AllNodes()
            )
        return TL.match(self._trace, global_filter, local_filters)

    def on_visit(self, node: CSTNodeT) -> bool:
        if isinstance(node, GenNode):
            self._trace.append(node.tag)
            return False
        else:
            self._trace.append(type(node))
            self.on_visit_pure_node(node)
            return True

    def on_leave(self, _node: CSTNodeT, node: CSTNodeT) -> CSTNodeT:
        if isinstance(node, GenNode):
            try:
                self.on_visit_gen_node(node)
            except Exception as e:
                raise UnexpectedFailure(e)
            while True:
                try:
                    self.trans_start()
                    self.on_visit_gen_func(node)
                    mid_node = node.generate(self)
                    self.on_leave_gen_func(node, mid_node)
                    self.on_visit_mid_node(mid_node)
                    new_node = mid_node.visit(self)
                    self.on_leave_mid_node(mid_node, new_node)
                    self.on_visit_node(new_node)
                    break
                except AllowableFailure as e:
                    self.trans_rollback()
                    if e.in_this_node:
                        pass
                    else:
                        e.emerge()
                        raise e from None
                else:
                    self.trans_fix()
            try:
                self.on_leave_node(new_node)
                self.on_leave_gen_node(node, new_node)
            except Exception as e:
                raise UnexpectedFailure(e)
            self._trace.pop()
            return new_node
        elif isinstance(node, CSTNode):
            self.on_leave_pure_node(node)
            self._trace.pop()
            return node
        else:
            raise TypeError(f"Argument isn't node because it has type {type(node)}")

    def trans_start(self) -> None:
        self._trans_list.clear()

    def trans_fix(self) -> None:
        pass

    def trans_rollback(self) -> None:
        for func in reversed(self._trans_list):
            func()

    def on_start_generation(self) -> None:
        for checker in self.checkers:
            checker.on_start_generation(self)

    def on_visit_gen_node(self, node: GenNode) -> None:
        for checker in self.checkers:
            checker.on_visit_gen_node(node, self)

    def on_leave_gen_node(self, node: GenNode, new_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_gen_node(node, new_node, self)

    def on_visit_gen_func(self, node: GenNode) -> None:
        for checker in self.checkers:
            checker.on_visit_gen_func(node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_gen_func(node, self)
            )

    def on_leave_gen_func(self, node: GenNode, mid_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_gen_func(node, mid_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unleave_gen_func(
                    node, mid_node, self
                )
            )

    def on_visit_mid_node(self, node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_mid_node(node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_mid_mode(node, self)
            )

    def on_leave_mid_node(self, node: CSTNodeT, new_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_mid_node(node, new_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unleave_mid_node(
                    node, new_node, self
                )
            )

    def on_visit_node(self, node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_node(node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_node(node, self)
            )

    def on_leave_node(self, node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_node(node, self)

    def on_visit_pure_node(self, node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_pure_node(node, self)

    def on_leave_pure_node(self, node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_pure_node(node, self)

    def on_visit_attribute(self, node: CSTNodeT, attr: str) -> None:
        for checker in self.checkers:
            checker.on_visit_attr(node, attr, self)

    def on_leave_attribute(self, node: CSTNodeT, attr: str) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_attr(node, attr, self)
