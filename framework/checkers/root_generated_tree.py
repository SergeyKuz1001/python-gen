from .abstract import AbstractChecker
from ._ghostmethod import ghostmethod

from abc import ABC
from libcst import CSTNode


class RootGeneratedTreeChecker(AbstractChecker, ABC):
    def start_generation(self, generator: "Generator"):
        self._depth: int = 0

    @ghostmethod
    def visit_root(self, root: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def leave_root(self, root: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unvisit_root(self, root: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unleave_root(self, root: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def revisit_root(self, root: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def releave_root(self, root: CSTNode, generator: "Generator") -> None: ...

    def on_visit_mid_node(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> None:
        if self._depth == 0:
            visit = getattr(self, "visit_root", None)
            if visit is not None:
                visit(mid_node, generator)
            else:
                visit = getattr(self, "revisit_root", None)
                if visit is not None:
                    visit(mid_node, generator)
        self._depth += 1
        super().on_visit_mid_node(mid_node, generator)

    def on_leave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        self._depth -= 1
        if self._depth == 0:
            leave = getattr(self, "leave_root", None)
            if leave is not None:
                leave(new_node, generator)
            else:
                leave = getattr(self, "releave_root", None)
                if leave is not None:
                    leave(new_node, generator)
        super().on_leave_mid_node(mid_node, new_node, generator)

    def on_unvisit_mid_node(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> None:
        self._depth -= 1
        if self._depth == 0:
            unvisit = getattr(self, "unvisit_root", None)
            if unvisit is not None:
                unvisit(mid_node, generator)
            else:
                unvisit = getattr(self, "releave_root", None)
                if unvisit is not None:
                    unvisit(mid_node, generator)
        super().on_unvisit_mid_node(mid_node, generator)

    def on_unleave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        if self._depth == 0:
            unleave = getattr(self, "unleave_root", None)
            if unleave is not None:
                unleave(new_node, generator)
            else:
                unleave = getattr(self, "revisit_root", None)
                if unleave is not None:
                    unleave(new_node, generator)
        self._depth += 1
        super().on_unleave_mid_node(mid_node, new_node, generator)
