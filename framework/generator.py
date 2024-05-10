from .gen_node import GenNode
from .choose import Choose
from .checkers import AbstractChecker, RuleChecker
from .failures import AllowableFailure, UnexpectedFailure
from .trace_language import AbstractFilter, GlobalFilter, OnlyGenNodes, AllNodes, is_matched

from dataclasses import dataclass
from types import FunctionType
from typing import Optional, Union, Callable
from libcst import CSTTransformer, CSTNode, CSTNodeT


@dataclass(frozen=True)
class Generator(CSTTransformer):
    choose: Choose
    grammar: "Grammar"
    checkers: list[AbstractChecker]

    def __init__(self, seed: int, grammar: "Grammar", checkers: list[AbstractChecker]):
        object.__setattr__(self, "choose", Choose(seed))
        object.__setattr__(self, "grammar", grammar)
        object.__setattr__(self, "checkers", checkers)
        object.__setattr__(self, "_trace", [])
        object.__setattr__(self, "_trans_list", [])
        object.__setattr__(self, "_code", None)

    @property
    def code(self) -> str:
        if self._code is None:
            self._on_start_generation()
            object.__setattr__(self, "_code", self.grammar.start.visit(self).code)
        return self._code

    @property
    def rule_checkers(self) -> list[RuleChecker]:
        return list(filter(lambda checker: isinstance(checker, RuleChecker), self.checkers))

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

    @property
    def identifier(self) -> str:
        return self.grammar.identifier + "_" + str(self.choose.seed) + "".join(map(lambda checker: "_" + checker.identifier, self.checkers))

    def on_trace(self, *local_filters) -> bool:
        if isinstance(local_filters[0], GlobalFilter):
            global_filter, local_filters = local_filters[0], local_filters[1:]
        else:
            global_filter = (
                OnlyGenNodes()
                if all(
                    map(
                        lambda lf: type(lf) == str or isinstance(lf, AbstractFilter),
                        local_filters,
                    )
                )
                else AllNodes()
            )
        return is_matched(self._trace, global_filter, local_filters)

    def on_visit(self, node: CSTNodeT) -> bool:
        if isinstance(node, GenNode):
            self._trace.append(node.tag)
            return False
        elif isinstance(node, CSTNode):
            self._trace.append(type(node))
            self._on_visit_pure_node(node)
            return True
        else:
            raise TypeError(f"Argument isn't node because it has type {type(node)}")

    def on_leave(self, _node: CSTNodeT, node: CSTNodeT) -> CSTNodeT:
        if isinstance(node, GenNode):
            try:
                self._on_visit_gen_node(node)
            except Exception as e:
                raise UnexpectedFailure(e)
            while True:
                try:
                    self._trans_start()
                    self._on_visit_gen_func(node)
                    mid_node = node.generate(self)
                    self._on_leave_gen_func(node, mid_node)
                    self._on_visit_mid_node(mid_node)
                    new_node = mid_node.visit(self)
                    self._on_leave_mid_node(mid_node, new_node)
                    self._on_visit_node(new_node)
                    break
                except AllowableFailure as e:
                    self._trans_rollback()
                    if e.in_this_node:
                        pass
                    else:
                        e.emerge()
                        raise e from None
                else:
                    self._trans_fix()
            try:
                self._on_leave_node(new_node)
                self._on_leave_gen_node(node, new_node)
            except Exception as e:
                raise UnexpectedFailure(e)
            self._trace.pop()
            return new_node
        elif isinstance(node, CSTNode):
            self._on_leave_pure_node(node)
            self._trace.pop()
            return node
        else:
            raise TypeError(f"Argument isn't node because it has type {type(node)}")

    def _trans_start(self) -> None:
        self._trans_list.clear()

    def _trans_fix(self) -> None:
        pass

    def _trans_rollback(self) -> None:
        for func in reversed(self._trans_list):
            func()

    def _on_start_generation(self) -> None:
        for checker in self.checkers:
            checker.on_start_generation(self)

    def _on_visit_gen_node(self, node: GenNode) -> None:
        for checker in self.checkers:
            checker.on_visit_gen_node(node, self)

    def _on_leave_gen_node(self, node: GenNode, new_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_gen_node(node, new_node, self)

    def _on_visit_gen_func(self, node: GenNode) -> None:
        for checker in self.checkers:
            checker.on_visit_gen_func(node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_gen_func(node, self)
            )

    def _on_leave_gen_func(self, node: GenNode, mid_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_gen_func(node, mid_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unleave_gen_func(
                    node, mid_node, self
                )
            )

    def _on_visit_mid_node(self, mid_node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_mid_node(mid_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_mid_mode(mid_node, self)
            )

    def _on_leave_mid_node(self, mid_node: CSTNodeT, new_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_mid_node(mid_node, new_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unleave_mid_node(
                    mid_node, new_node, self
                )
            )

    def _on_visit_node(self, new_node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_node(new_node, self)
            self._trans_list.append(
                lambda checker=checker: checker.on_unvisit_node(new_node, self)
            )

    def _on_leave_node(self, new_node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_node(new_node, self)

    def _on_visit_pure_node(self, node: CSTNodeT) -> None:
        for checker in self.checkers:
            checker.on_visit_pure_node(node, self)

    def _on_leave_pure_node(self, node: CSTNodeT) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_pure_node(node, self)

    def _on_visit_attribute(self, node: CSTNodeT, attr: str) -> None:
        for checker in self.checkers:
            checker.on_visit_attr(node, attr, self)

    def _on_leave_attribute(self, node: CSTNodeT, attr: str) -> None:
        for checker in reversed(self.checkers):
            checker.on_leave_attr(node, attr, self)
