from abc import ABC, abstractmethod
from libcst import CSTNode
from typing import Optional, Callable


def ghostmethod(func: Callable) -> Callable:
    return None


class AbstractChecker(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str: ...

    @ghostmethod
    def start_generation(self, generator: "Generator") -> None: ...

    @ghostmethod
    def visit_gen_node(self, node: "GenNode", generator: "Generator") -> None: ...

    @ghostmethod
    def leave_gen_node(self, node: "GenNode", new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def visit_gen_func(self, node: "GenNode", generator: "Generator") -> None: ...

    @ghostmethod
    def leave_gen_func(self, node: "GenNode", mid_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unvisit_gen_func(self, node: "GenNode", generator: "Generator") -> None: ...

    @ghostmethod
    def unleave_gen_func(self, node: "GenNode", mid_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def revisit_gen_func(self, node: "GenNode", mid_node: Optional[CSTNode], generator: "Generator") -> None: ...

    @ghostmethod
    def releave_gen_func(self, node: "GenNode", mid_node: Optional[CSTNode], generator: "Generator") -> None: ...

    @ghostmethod
    def visit_mid_node(self, mid_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def leave_mid_node(self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unvisit_mid_node(self, mid_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unleave_mid_node(self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def revisit_mid_node(self, mid_node: CSTNode, new_node: Optional[CSTNode], generator: "Generator") -> None: ...

    @ghostmethod
    def releave_mid_node(self, mid_node: CSTNode, new_node: Optional[CSTNode], generator: "Generator") -> None: ...

    @ghostmethod
    def visit_node(self, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def leave_node(self, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def unvisit_node(self, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def releave_node(self, new_node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def visit_pure_node(self, node: CSTNode, generator: "Generator") -> None: ...

    @ghostmethod
    def leave_pure_node(self, node: CSTNode, generator: "Generator") -> None: ...

    def on_start_generation(self, generator: "Generator") -> None:
        start = getattr(self, "start_generation", None)
        if start is not None:
            start(generator)

    def on_visit_gen_node(self, node: "GenNode", generator: "Generator") -> None:
        visit = getattr(self, f"visit_gen_node", None)
        if visit is not None:
            visit(node, generator)

    def on_leave_gen_node(
        self, node: "GenNode", new_node: CSTNode, generator: "Generator"
    ) -> None:
        leave = getattr(self, f"leave_gen_node", None)
        if leave is not None:
            leave(node, new_node, generator)

    def on_visit_gen_func(self, node: "GenNode", generator: "Generator") -> None:
        visit = getattr(self, f"visit_gen_func", None)
        if visit is not None:
            visit(node, generator)
            return
        visit = getattr(self, f"revisit_gen_func", None)
        if visit is not None:
            visit(node, None, generator)

    def on_leave_gen_func(
        self, node: "GenNode", mid_node: CSTNode, generator: "Generator"
    ) -> None:
        leave = getattr(self, f"leave_gen_func", None)
        if leave is not None:
            leave(node, mid_node, generator)
            return
        leave = getattr(self, f"releave_gen_func", None)
        if leave is not None:
            leave(node, mid_node, generator)

    def on_visit_mid_node(self, mid_node: CSTNode, generator: "Generator") -> None:
        visit = getattr(self, f"visit_mid_node", None)
        if visit is not None:
            visit(mid_node, generator)
            return
        visit = getattr(self, f"revisit_mid_node", None)
        if visit is not None:
            visit(mid_node, None, generator)

    def on_leave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        leave = getattr(self, f"leave_mid_node", None)
        if leave is not None:
            leave(mid_node, new_node, generator)
            return
        leave = getattr(self, f"releave_mid_node", None)
        if leave is not None:
            leave(mid_node, new_node, generator)

    def on_visit_node(self, new_node: CSTNode, generator: "Generator") -> None:
        visit = getattr(self, f"visit_node", None)
        if visit is not None:
            visit(new_node, generator)

    def on_leave_node(self, new_node: CSTNode, generator: "Generator") -> None:
        leave = getattr(self, f"leave_node", None)
        if leave is not None:
            leave(new_node, generator)
            return
        leave = getattr(self, f"releave_node", None)
        if leave is not None:
            leave(new_node, generator)

    def on_visit_pure_node(self, node: CSTNode, generator: "Generator") -> None:
        visit = getattr(self, f"visit_pure_node", None)
        if visit is not None:
            visit(node, generator)

    def on_leave_pure_node(self, node: CSTNode, generator: "Generator") -> None:
        leave = getattr(self, f"leave_pure_node", None)
        if leave is not None:
            leave(node, generator)

    def on_visit_attr(self, node: CSTNode, attr: str, generator: "Generator") -> None:
        pass

    def on_leave_attr(self, node: CSTNode, attr: str, generator: "Generator") -> None:
        pass

    def on_unvisit_gen_func(self, node: "GenNode", generator: "Generator") -> None:
        unvisit = getattr(self, f"unvisit_gen_func", None)
        if unvisit is not None:
            unvisit(node, generator)
            return
        unvisit = getattr(self, f"releave_gen_func", None)
        if unvisit is not None:
            unvisit(node, None, generator)

    def on_unleave_gen_func(
        self, node: "GenNode", mid_node: CSTNode, generator: "Generator"
    ) -> None:
        unleave = getattr(self, f"unleave_gen_func", None)
        if unleave is not None:
            unleave(node, mid_node, generator)
            return
        unleave = getattr(self, f"revisit_gen_func", None)
        if unleave is not None:
            unleave(node, mid_node, generator)

    def on_unvisit_mid_node(self, mid_node: CSTNode, generator: "Generator") -> None:
        unvisit = getattr(self, f"unvisit_mid_node", None)
        if unvisit is not None:
            unvisit(mid_node, generator)
            return
        unvisit = getattr(self, f"releave_mid_node", None)
        if unvisit is not None:
            unvisit(mid_node, None, generator)

    def on_unleave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        unleave = getattr(self, f"unleave_mid_node", None)
        if unleave is not None:
            unleave(mid_node, new_node, generator)
            return
        unleave = getattr(self, f"revisit_mid_node", None)
        if unleave is not None:
            unleave(mid_node, new_node, generator)

    def on_unvisit_node(self, new_node: CSTNode, generator: "Generator") -> None:
        unvisit = getattr(self, f"unvisit_node", None)
        if unvisit is not None:
            unvisit(new_node, generator)
            return
        unvisit = getattr(self, f"releave_node", None)
        if unvisit is not None:
            unvisit(new_node, generator)
