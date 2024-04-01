from abstract_checker import AbstractChecker
from state_via_mid_rec_checker import StateViaMidRecChecker
from gen_node import GenNode
from generator import Generator
from config import Alternatives, GenGetter

from dataclasses import dataclass
from libcst import CSTNode
from typing import Union, Optional


@dataclass()
class TreeDepthChecker(StateViaMidRecChecker):
    accounted_nodes: dict[str, dict[str, int]]
    border: int
    current_score: int = 0

    def __post_init__(self):
        super().__init__()

    def visit_gen_func(self, node: GenNode, generator: Generator, *args) -> None:
        if len(args) == 1:
            generator = args[0]
        if (
            node.tag in self.accounted_nodes
            and type(generator.config[node.tag]) == Alternatives
        ):
            self._is_accounted_node = True
            self._saved_node_config = generator.config[node.tag]
            self._accounted_tags = self.accounted_nodes[node.tag]
            self._chosen_alt_tag = None
            if self.current_score < self.border:
                generator.config[node.tag] = Alternatives(
                    {
                        tag: [
                            w,
                            (
                                GenGetter(
                                    lambda generator, tag=tag: (
                                        part,
                                        generator.find_checker(type(self)).__setattr__(
                                            "_chosen_alt_tag", tag
                                        ),
                                    )[0]
                                )
                                if tag in self._accounted_tags
                                else part
                            ),
                        ]
                        for tag, (w, part) in self._saved_node_config.alts.items()
                    }
                )
            else:
                generator.config[node.tag] = Alternatives(
                    {
                        tag: w_part
                        for tag, w_part in filter(
                            lambda p: p[0] not in self._accounted_tags,
                            self._saved_node_config.alts.items(),
                        )
                    }
                )
        else:
            self._is_accounted_node = False

    def releave_gen_func(self, node: GenNode, generator: Generator, *args) -> None:
        if len(args) == 1:
            generator = args[0]
        if self._is_accounted_node:
            generator.config[node.tag] = self._saved_node_config

    def revisit_mid_node(self, node: CSTNode, generator: Generator, *args) -> None:
        if self._is_accounted_node and self._chosen_alt_tag is not None:
            weight = self._accounted_tags[self._chosen_alt_tag]
            self.current_score += weight
            self.state = (True, weight)
        else:
            self.state = (False, None)

    def releave_mid_node(self, node: CSTNode, generator: Generator, *args) -> None:
        is_accounted_node, weight = self.state
        if is_accounted_node:
            self.current_score -= weight
