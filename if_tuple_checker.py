from abstract_checker import AbstractChecker
from rule_checker import RuleChecker
from gen_node import GenNode
from generator import Generator, TL
from failures import AllowableFailure, UnexpectedFailure
from config import LambdaConst, Constructor, ListDescriptor, Alternatives, GenGetter

from libcst import (
    If,
    Tuple,
    IndentedBlock,
    Element,
    Integer,
    Module,
    CSTNode,
    CSTTransformer,
)
from typing import Optional, Callable


class IfTuple:
    rule: str = "F634"

    class With:
        class MaybeIfBlockAtTheEndChecker(RuleChecker):
            def __init__(self):
                self._if_tuple_already_exists: bool = False

            def in_rules(self, rules: list[str], generator: Generator) -> bool:
                return IfTuple.rule in rules

            def start_generation(self, generator: Generator) -> None:
                generator.config["it_mibate__if_block"] = LambdaConst(
                    lambda: If(Tuple([Element(Integer("0"))]), IndentedBlock([]))
                )

            def revisit_gen_func(
                self, node: CSTNode, generator: Generator, *args
            ) -> None:
                if len(args) == 1:
                    mid_node, generator = generator, args[0]
                if (
                    generator.on_trace("module", "indented_block")
                    and not self._if_tuple_already_exists
                ):
                    self._saved_config_indented_block = generator.config.get(
                        "indented_block"
                    )
                    if (
                        self._saved_config_indented_block is None
                        or type(self._saved_config_indented_block) != Constructor
                        or self._saved_config_indented_block.init != IndentedBlock
                        or "body" not in self._saved_config_indented_block.kwargs
                        or type(self._saved_config_indented_block.kwargs["body"])
                        != ListDescriptor
                    ):
                        raise UnexpectedFailure(
                            "Unexpected structure of indented_block GenNode"
                        )
                    generator.config["indented_block"] = Constructor(
                        IndentedBlock,
                        body=ListDescriptor(
                            lambda choose: self._saved_config_indented_block.kwargs[
                                "body"
                            ].size(choose)
                            + 1,
                            lambda index, length: (
                                self._saved_config_indented_block.kwargs["body"].elem(
                                    index, length - 1
                                )
                                if index + 1 != length
                                else LambdaConst(GenNode, "it_mibate__if_block")
                            ),
                        ),
                    )

            def releave_gen_func(
                self, node: CSTNode, generator: Generator, *args
            ) -> None:
                if len(args) == 1:
                    mid_node, generator = generator, args[0]
                if (
                    generator.on_trace("module", "indented_block")
                    and not self._if_tuple_already_exists
                ):
                    generator.config["indented_block"] = (
                        self._saved_config_indented_block
                    )

            def leave_pure_node(self, node: CSTNode, generator: Generator) -> None:
                if (
                    generator.on_trace(If, "base_expression", "tuple", Tuple)
                    and len(node.elements) > 0
                ):
                    self._if_tuple_already_exists = True

    class Without:
        class DeleteTupleFromConfigChecker(RuleChecker):
            def in_rules(self, rules: list[str], generator: Generator) -> bool:
                return IfTuple.rule not in rules

            def revisit_gen_func(
                self, node: CSTNode, generator: Generator, *args
            ) -> None:
                if len(args) == 1:
                    mid_node, generator = generator, args[0]
                if generator.on_trace("if_block", "base_expression"):
                    config_base_expression = generator.config.get("base_expression")
                    if (
                        config_base_expression is None
                        or type(config_base_expression) != Alternatives
                        or "tuple" not in config_base_expression.alts
                    ):
                        raise UnexpectedFailure(
                            "Unexpected structure of base_expression GenNode"
                        )
                    self._saved_part_of_tuple = config_base_expression.alts["tuple"]
                    del generator.config["base_expression"].alts["tuple"]

            def releave_gen_func(
                self, node: CSTNode, generator: Generator, *args
            ) -> None:
                if len(args) == 1:
                    mid_node, generator = generator, args[0]
                if generator.on_trace("if_block", "base_expression"):
                    generator.config["base_expression"].alts[
                        "tuple"
                    ] = self._saved_part_of_tuple
