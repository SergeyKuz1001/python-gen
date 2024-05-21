from .abstract import AbstractChecker
from ._ghostmethod import ghostmethod

from abc import ABC
from libcst import CSTNode
from typing import Optional


class StateViaMidRecChecker(AbstractChecker, ABC):
    def start_generation(self, generator: "Generator") -> None:
        self._states: list[any] = []

    @ghostmethod
    def visit_mid_node_with_state(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> any: ...

    @ghostmethod
    def leave_mid_node_with_state(
        self,
        mid_node: CSTNode,
        new_node: CSTNode,
        generator: "Generator",
        state: any,
    ) -> None: ...

    @ghostmethod
    def unvisit_mid_node_with_state(
        self, mid_node: CSTNode, generator: "Generator", state: any
    ) -> None: ...

    @ghostmethod
    def unleave_mid_node_with_state(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> any: ...

    @ghostmethod
    def revisit_mid_node_with_state(
        self,
        mid_node: CSTNode,
        new_node: Optional[CSTNode],
        generator: "Generator",
    ) -> any: ...

    @ghostmethod
    def releave_mid_node_with_state(
        self,
        mid_node: CSTNode,
        new_node: Optional[CSTNode],
        generator: "Generator",
        state: any,
    ) -> None: ...

    def on_visit_mid_node(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> None:
        visit = getattr(self, "visit_mid_node_with_state", None)
        if visit is not None:
            self._states.append(visit(mid_node, generator))
            return
        visit = getattr(self, "revisit_mid_node_with_state", None)
        if visit is not None:
            self._states.append(visit(mid_node, None, generator))

    def on_leave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        leave = getattr(self, "leave_mid_node_with_state", None)
        if leave is not None:
            leave(mid_node, new_node, generator, self._states.pop())
            return
        leave = getattr(self, "releave_mid_node_with_state", None)
        if leave is not None:
            leave(mid_node, new_node, generator, self._states.pop())

    def on_unvisit_mid_node(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> None:
        unvisit = getattr(self, "unvisit_mid_node_with_state", None)
        if unvisit is not None:
            unvisit(mid_node, generator, self._states.pop())
            return
        unvisit = getattr(self, "releave_mid_node_with_state", None)
        if unvisit is not None:
            unvisit(mid_node, None, generator, self._states.pop())

    def on_unleave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        unleave = getattr(self, "unleave_mid_node_with_state", None)
        if unleave is not None:
            self._states.append(unleave(mid_node, new_node, generator))
            return
        unleave = getattr(self, "revisit_mid_node_with_state", None)
        if unleave is not None:
            self._states.append(unleave(mid_node, new_node, generator))

    @property
    def state(self) -> any:
        return self._states.pop()

    @state.setter
    def state(self, value: any) -> None:
        return self._states.append(value)
