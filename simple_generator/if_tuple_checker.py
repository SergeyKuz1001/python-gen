from framework import *

from typing import Optional, Callable


class IfTuple:
    rule: str = "F634"

    class With:
        class MaybeIfBlockAtTheEndChecker(RuleChecker):
            def __init__(self):
                self._if_tuple_already_exists: bool = False

            def in_rules(self, rules: list[str]) -> bool:
                return IfTuple.rule in rules

            @property
            def identifier(self) -> str:
                return "+it"

            def start_generation(self, generator: Generator) -> None:
                generator.grammar["it_mibate__if_block"] = LambdaConst(
                    lambda: If(Tuple([Element(Integer("0"))]), IndentedBlock([]))
                )

            def revisit_gen_func(
                self, node: GenNode, mid_node: Optional[CSTNode], generator: Generator
            ) -> None:
                if (
                    generator.on_trace("module", "indented_block")
                    and not self._if_tuple_already_exists
                ):
                    rule = generator.grammar["indented_block"]
                    if (
                        rule is None
                        or type(rule) != Constructor
                        or rule.init != IndentedBlock
                        or "body" not in rule.kwargs
                        or type(rule.kwargs["body"]) != ListDescriptor
                    ):
                        raise UnexpectedFailure(
                            "Unexpected structure of indented_block GenNode"
                        )
                    generator.grammar["indented_block"] = Constructor(
                        IndentedBlock,
                        body=ListDescriptor(
                            lambda choose: rule.kwargs["body"].size(choose) + 1,
                            lambda index, length: (
                                rule.kwargs["body"].elem(index, length - 1)
                                if index + 1 != length
                                else LambdaConst(GenNode, "it_mibate__if_block")
                            ),
                        ),
                    )

            def releave_gen_func(
                self, node: GenNode, mid_node: Optional[CSTNode], generator: Generator
            ) -> None:
                if (
                    generator.on_trace("module", "indented_block")
                    and not self._if_tuple_already_exists
                ):
                    del generator.grammar["indented_block"]

            def leave_pure_node(self, node: CSTNode, generator: Generator) -> None:
                if (
                    generator.on_trace(If, "base_expression", "tuple", Tuple)
                    and len(node.elements) > 0
                ):
                    self._if_tuple_already_exists = True

    class Without:
        class DeleteTupleFromConfigChecker(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return IfTuple.rule not in rules

            @property
            def identifier(self) -> str:
                return "-it"

            def revisit_gen_func(
                self, node: GenNode, mid_node: Optional[CSTNode], generator: Generator
            ) -> None:
                if generator.on_trace("if_block", "base_expression"):
                    rule = generator.grammar["base_expression"]
                    if (
                        rule is None
                        or type(rule) != Alternatives
                        or "tuple" not in rule.alts
                    ):
                        raise UnexpectedFailure(
                            "Unexpected structure of base_expression GenNode"
                        )
                    self._saved_part_of_tuple = rule.alts["tuple"]
                    del generator.grammar["base_expression"].alts["tuple"]

            def releave_gen_func(
                self, node: GenNode, mid_node: Optional[CSTNode], generator: "Generator"
            ) -> None:
                if generator.on_trace("if_block", "base_expression"):
                    generator.grammar["base_expression"].alts[
                        "tuple"
                    ] = self._saved_part_of_tuple
