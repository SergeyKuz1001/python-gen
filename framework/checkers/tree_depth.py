from .state_via_mid_rec import StateViaMidRecChecker

from ..grammar import Alternatives, GenGetter

from dataclasses import dataclass
from libcst import CSTNode
from typing import Union, Optional


@dataclass()
class TreeDepthChecker(StateViaMidRecChecker):
    accounted_nodes: dict[str, dict[str, int]]
    border: int
    current_score: int = 0
    _identifier: Optional[str] = None

    def __post_init__(self):
        super().__init__()

    @property
    def identifier(self) -> str:
        if self._identifier is None:
            return "+" + str(self.border) + "+" + "--".join(sorted(node + "-" + alt + "-" + str(count) for node, accounted_alts in self.accounted_nodes.items() for alt, count in accounted_alts.items())) + "+"
        else:
            return self._identifier

    @identifier.setter
    def identifier(self, value: str) -> None:
        self._identifier = value

    def revisit_gen_func(self, node: "GenNode", mid_node: Optional[CSTNode], generator: "Generator") -> None:
        if (
            node.tag in self.accounted_nodes
            and type(generator.grammar[node.tag]) == Alternatives
        ):
            self._is_accounted_node = True
            rule = generator.grammar[node.tag]
            self._accounted_tags = self.accounted_nodes[node.tag]
            self._chosen_alt_tag = None
            if self.current_score < self.border:
                generator.grammar[node.tag] = Alternatives(
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
                        for tag, (w, part) in rule.alts.items()
                    }
                )
            else:
                generator.grammar[node.tag] = Alternatives(
                    {
                        tag: w_part
                        for tag, w_part in filter(
                            lambda p: p[0] not in self._accounted_tags,
                            rule.alts.items(),
                        )
                    }
                )
        else:
            self._is_accounted_node = False

    def releave_gen_func(self, node: "GenNode", mid_node: Optional[CSTNode], generator: "Generator") -> None:
        if self._is_accounted_node:
            del generator.grammar[node.tag]

    def revisit_mid_node(self, mid_node: CSTNode, new_node: Optional[CSTNode], generator: "Generator") -> None:
        if self._is_accounted_node and self._chosen_alt_tag is not None:
            weight = self._accounted_tags[self._chosen_alt_tag]
            self.current_score += weight
            self.state = (True, weight)
        else:
            self.state = (False, None)

    def releave_mid_node(self, mid_node: CSTNode, new_node: Optional[CSTNode], generator: "Generator") -> None:
        is_accounted_node, weight = self.state
        if is_accounted_node:
            self.current_score -= weight
