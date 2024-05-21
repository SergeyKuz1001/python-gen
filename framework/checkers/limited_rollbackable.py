from .abstract import AbstractChecker

from ..trace_language import AbstractFilter
from ..failures import UnexpectedFailure

from abc import ABC
from libcst import CSTNode
from typing import Callable


class LimitedRollbackableChecker(AbstractChecker, ABC):
    @property
    def unvisit_gen_func_methods(
        self,
    ) -> list[
        tuple[list[AbstractFilter], Callable[["GenNode", "Generator"], None]]
    ]:
        return []

    @property
    def unleave_gen_func_methods(
        self,
    ) -> list[
        tuple[
            list[AbstractFilter],
            Callable[["GenNode", CSTNode, "Generator"], None],
        ]
    ]:
        return []

    @property
    def unvisit_mid_node_methods(
        self,
    ) -> list[
        tuple[list[AbstractFilter], Callable[[CSTNode, "Generator"], None]]
    ]:
        return []

    @property
    def unleave_mid_node_methods(
        self,
    ) -> list[
        tuple[
            list[AbstractFilter],
            Callable[[CSTNode, CSTNode, "Generator"], None],
        ]
    ]:
        return []

    @property
    def unvisit_node_methods(
        self,
    ) -> list[
        tuple[list[AbstractFilter], Callable[[CSTNode, "Generator"], None]]
    ]:
        return []

    def on_unvisit_gen_func(
        self, node: "GenNode", generator: "Generator"
    ) -> None:
        for trace, func in self.unvisit_gen_func_methods:
            if generator.on_trace(*trace):
                func(node, generator)
                return
        for trace, _ in self.unleave_gen_func_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unvisit_mid_node_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unleave_mid_node_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unvisit_node_methods:
            if generator.on_trace(*trace):
                return
        raise UnexpectedFailure(
            f"checker {self.identifier} hasn't handler for unvisit_gen_func"
        )

    def on_unleave_gen_func(
        self, node: "GenNode", mid_node: CSTNode, generator: "Generator"
    ) -> None:
        for trace, func in self.unleave_gen_func_methods:
            if generator.on_trace(*trace):
                func(node, mid_node, generator)
                return
        for trace, _ in self.unvisit_mid_node_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unleave_mid_node_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unvisit_node_methods:
            if generator.on_trace(*trace):
                return
        raise UnexpectedFailure(
            f"checker {self.identifier} hasn't handler for unleave_gen_func"
        )

    def on_unvisit_mid_node(
        self, mid_node: CSTNode, generator: "Generator"
    ) -> None:
        for trace, func in self.unvisit_mid_node_methods:
            if generator.on_trace(*trace):
                func(mid_node, generator)
                return
        for trace, _ in self.unleave_mid_node_methods:
            if generator.on_trace(*trace):
                return
        for trace, _ in self.unvisit_node_methods:
            if generator.on_trace(*trace):
                return
        raise UnexpectedFailure(
            f"checker {self.identifier} hasn't handler for unvisit_mid_node"
        )

    def on_unleave_mid_node(
        self, mid_node: CSTNode, new_node: CSTNode, generator: "Generator"
    ) -> None:
        for trace, func in self.unleave_mid_node_methods:
            if generator.on_trace(*trace):
                func(mid_node, new_node, generator)
                return
        for trace, _ in self.unvisit_node_methods:
            if generator.on_trace(*trace):
                return
        raise UnexpectedFailure(
            f"checker {self.identifier} hasn't handler for unleave_mid_node"
        )

    def on_unvisit_node(
        self, new_node: CSTNode, generator: "Generator"
    ) -> None:
        for trace, func in self.unvisit_node_methods:
            if generator.on_trace(*trace):
                func(new_node, generator)
                return
        raise UnexpectedFailure(
            f"checker {self.identifier} hasn't handler for unvisit_node"
        )
