from framework import *

from typing import Optional


class IfTuple:
    rule: str = "F634"

    class With:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return IfTuple.rule in rules

        class MaybeIfBlockAtTheEndChecker(_Base):
            @property
            def identifier(self) -> str:
                return "+it"

            def start_generation(self, generator: Generator) -> None:
                self._if_tuple_already_exists: bool = False
                generator.grammar["it_mibate__if_block"] = LambdaConst(
                    lambda: If(
                        Tuple([Element(Integer("0"))]), IndentedBlock([])
                    )
                )

            def revisit_gen_func(
                self,
                node: GenNode,
                mid_node: Optional[CSTNode],
                generator: Generator,
            ) -> None:
                if (
                    generator.on_trace("main_block", "indented_block")
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
                self,
                node: GenNode,
                mid_node: Optional[CSTNode],
                generator: Generator,
            ) -> None:
                if (
                    generator.on_trace("main_block", "indented_block")
                    and not self._if_tuple_already_exists
                ):
                    del generator.grammar["indented_block"]

            def leave_pure_node(
                self, node: CSTNode, generator: Generator
            ) -> None:
                if (
                    generator.on_trace(If, "base_expression", "tuple", Tuple)
                    and len(node.elements) > 0
                ):
                    self._if_tuple_already_exists = True

        class ContainsPredicateChecker(_Base, PredicateChecker):
            @property
            def identifier(self) -> str:
                return "+it-pr"

            class InternalVisitor(CSTVisitor):
                def __init__(self):
                    self.if_tuple_found: bool = False

                def on_visit(self, node: CSTNode) -> bool:
                    return not self.if_tuple_found

                def on_leave(self, original_node: CSTNode) -> None:
                    pass

                def on_visit_attribute(
                    self, node: CSTNode, attribute: str
                ) -> None:
                    if (
                        type(node) == If
                        and attribute == "test"
                        and type(node.test) == Tuple
                        and len(node.test.elements) > 0
                    ):
                        self.if_tuple_found = True

                def on_leave_attribute(
                    self, original_node: CSTNode, attribute: str
                ) -> None:
                    pass

            def predicate(self, tree: CSTNode) -> bool:
                visitor = self.InternalVisitor()
                tree.visit(visitor)
                return visitor.if_tuple_found

    class Without:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return IfTuple.rule not in rules

        class DeleteTupleFromGrammarChecker(_Base):
            @property
            def identifier(self) -> str:
                return "-it"

            def revisit_gen_func(
                self,
                node: GenNode,
                mid_node: Optional[CSTNode],
                generator: Generator,
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
                    self._saved_part_tuple = rule.alts["tuple"]
                    del rule.alts["tuple"]

            def releave_gen_func(
                self,
                node: GenNode,
                mid_node: Optional[CSTNode],
                generator: "Generator",
            ) -> None:
                if generator.on_trace("if_block", "base_expression"):
                    generator.grammar["base_expression"].alts[
                        "tuple"
                    ] = self._saved_part_tuple

        class ChangeGrammarForIfChecker(_Base):
            @property
            def identifier(self) -> str:
                return "-it-ch"

            def start_generation(self, generator: Generator) -> None:
                if_rule = generator.grammar["if_block"]
                if (
                    if_rule is None
                    or type(if_rule) != Constructor
                    or if_rule.init != If
                    or "test" not in if_rule.kwargs
                    or "body" not in if_rule.kwargs
                    or type(if_rule.kwargs["test"]) != LambdaConst
                    or if_rule.kwargs["test"].init != GenNode
                    or len(if_rule.kwargs["test"].args) != 1
                    or if_rule.kwargs["test"].args[0] != "base_expression"
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of if_block GenNode"
                    )
                generator.grammar["if_block"] = Constructor(
                    If,
                    test=LambdaConst(
                        GenNode, "it_cgfi__if_condition_expression"
                    ),
                    body=if_rule.kwargs["body"],
                )
                be_rule = generator.grammar["base_expression"]
                if (
                    be_rule is None
                    or type(be_rule) != Alternatives
                    or "tuple" not in be_rule.alts
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of base_expression GenNode"
                    )
                generator.grammar["it_cgfi__if_condition_expression"] = (
                    Alternatives(
                        {
                            tag: (
                                part
                                if tag != "tuple"
                                else [part[0], LambdaConst(Tuple, [])]
                            )
                            for tag, part in be_rule.alts.items()
                        }
                    )
                )

        class DeleteIfWithTupleChecker(_Base):
            @property
            def identifier(self) -> str:
                return "-it-ld"

            def leave_mid_node(
                self, mid_node: CSTNode, new_node: CSTNode, generator: Generator
            ) -> None:
                if (
                    type(new_node) == If
                    and type(new_node.test) == Tuple
                    and len(new_node.test.elements) > 0
                ):
                    raise AllowableFailure()
