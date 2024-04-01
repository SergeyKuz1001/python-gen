from gen_node import GenNode

from abc import ABC
from libcst import CSTNode


class AbstractChecker(ABC):
    def on_start_generation(self, generator: "Generator") -> None:
        starts = [getattr(self, "start_generation", None)]
        for start in starts:
            if start is not None:
                start(generator)
                break

    def on_visit_gen_node(self, node: GenNode, generator: "Generator") -> None:
        visits = [
            getattr(self, f"visit_gen_node_{node.tag}", None),
            getattr(self, f"visit_gen_node", None),
        ]
        for visit in visits:
            if visit is not None:
                visit(node, generator)
                break

    def on_leave_gen_node(
        self, node: GenNode, new_node: "CSTNode", generator: "Generator"
    ) -> None:
        leaves = [
            getattr(self, f"leave_gen_node_{node.tag}", None),
            getattr(self, f"leave_gen_node", None),
        ]
        for leave in leaves:
            if leave is not None:
                leave(node, new_node, generator)
                break

    def on_visit_gen_func(self, node: GenNode, generator: "Generator") -> None:
        visits = [
            getattr(self, f"visit_gen_func_{node.tag}", None),
            getattr(self, f"revisit_gen_func_{node.tag}", None),
            getattr(self, f"visit_gen_func", None),
            getattr(self, f"revisit_gen_func", None),
        ]
        for visit in visits:
            if visit is not None:
                visit(node, generator)
                break

    def on_leave_gen_func(
        self, node: GenNode, mid_node: "CSTNode", generator: "Generator"
    ) -> None:
        leaves = [
            getattr(self, f"leave_gen_func_{node.tag}", None),
            getattr(self, f"releave_gen_func_{node.tag}", None),
            getattr(self, f"leave_gen_func", None),
            getattr(self, f"releave_gen_func", None),
        ]
        for leave in leaves:
            if leave is not None:
                leave(node, mid_node, generator)
                break

    def on_visit_mid_node(self, node: "CSTNode", generator: "Generator") -> None:
        visits = [
            getattr(
                self,
                f"visit_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(
                self,
                f"revisit_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(self, f"visit_mid_node", None),
            getattr(self, f"revisit_mid_node", None),
        ]
        for visit in visits:
            if visit is not None:
                visit(node, generator)
                break

    def on_leave_mid_node(
        self, node: "CSTNode", new_node: "CSTNode", generator: "Generator"
    ) -> None:
        leaves = [
            getattr(
                self,
                f"leave_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(
                self,
                f"releave_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(self, f"leave_mid_node", None),
            getattr(self, f"releave_mid_node", None),
        ]
        for leave in leaves:
            if leave is not None:
                leave(node, new_node, generator)
                break

    def on_visit_node(self, node: "CSTNode", generator: "Generator") -> None:
        visits = [
            getattr(self, f"visit_{type(node).__name__}", None),
            getattr(self, f"visit_node", None),
        ]
        for visit in visits:
            if visit is not None:
                visit(node, generator)
                break

    def on_leave_node(self, node: "CSTNode", generator: "Generator") -> None:
        leaves = [
            getattr(self, f"leave_{type(node).__name__}", None),
            getattr(self, f"leave_node", None),
        ]
        for leave in leaves:
            if leave is not None:
                leave(node, generator)
                break

    def on_visit_pure_node(self, node: "CSTNode", generator: "Generator") -> None:
        visits = [
            getattr(self, f"visit_pure_{type(node).__name__}", None),
            getattr(self, f"visit_pure_node", None),
        ]
        for visit in visits:
            if visit is not None:
                visit(node, generator)
                break

    def on_leave_pure_node(self, node: "CSTNode", generator: "Generator") -> None:
        leaves = [
            getattr(self, f"leave_pure_{type(node).__name__}", None),
            getattr(self, f"leave_pure_node", None),
        ]
        for leave in leaves:
            if leave is not None:
                leave(node, generator)
                break

    def on_visit_attr(self, node: "CSTNode", attr: str, generator: "Generator") -> None:
        visit = getattr(self, f"visit_{type(node).__name__}_{attr}", None)
        if visit is not None:
            visit(node, generator)

    def on_leave_attr(self, node: "CSTNode", attr: str, generator: "Generator") -> None:
        leave = getattr(self, f"leave_{type(node).__name__}_{attr}", None)
        if leave is not None:
            leave(node, generator)

    def on_unvisit_gen_func(self, node: GenNode, generator: "Generator") -> None:
        unvisits = [
            getattr(self, f"unvisit_gen_func_{node.tag}", None),
            getattr(self, f"releave_gen_func_{node.tag}", None),
            getattr(self, f"unvisit_gen_func", None),
            getattr(self, f"releave_gen_func", None),
        ]
        for unvisit in unvisits:
            if unvisit is not None:
                unvisit(node, generator)
                break

    def on_unleave_gen_func(
        self, node: GenNode, mid_node: "CSTNode", generator: "Generator"
    ) -> None:
        unleaves = [
            getattr(self, f"unleave_gen_func_{node.tag}", None),
            getattr(self, f"revisit_gen_func_{node.tag}", None),
            getattr(self, f"unleave_gen_func", None),
            getattr(self, f"revisit_gen_func", None),
        ]
        for unleave in unleaves:
            if unleave is not None:
                unleave(node, mid_node, generator)
                break

    def on_unvisit_mid_node(self, node: GenNode, generator: "Generator") -> None:
        unvisits = [
            getattr(
                self,
                f"unvisit_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(
                self,
                f"releave_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(self, f"unvisit_mid_node", None),
            getattr(self, f"releave_mid_node", None),
        ]
        for unvisit in unvisits:
            if unvisit is not None:
                unvisit(node, generator)
                break

    def on_unleave_mid_node(
        self, node: GenNode, new_node: "CSTNode", generator: "Generator"
    ) -> None:
        unleaves = [
            getattr(
                self,
                f"unleave_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(
                self,
                f"revisit_mid_{type(node).__name__}{('_' + node.tag) if isinstance(node, GenNode) else ''}",
                None,
            ),
            getattr(self, f"unleave_mid_node", None),
            getattr(self, f"revisit_mid_node", None),
        ]
        for unleave in unleaves:
            if unleave is not None:
                unleave(node, new_node, generator)
                break

    def on_unvisit_node(self, node: "CSTNode", generator: "Generator") -> None:
        unvisits = [
            getattr(self, f"unvisit_{type(node).__name__}", None),
            getattr(self, f"unvisit_node", None),
        ]
        for unvisit in unvisits:
            if unvisit is not None:
                unvisit(node, generator)
                break
