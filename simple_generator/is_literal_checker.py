from framework import *

from typing import Optional


class IsLiteral:
    rule: str = "F632"

    class With:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return IsLiteral.rule in rules

        class ContainsPredicateChecker(_Base, PredicateChecker):
            @property
            def identifier(self) -> str:
                return "+il"

            class InternalVisitor(CSTVisitor):
                def __init__(self):
                    self.is_literal_found: bool = False

                def on_visit(self, node: CSTNode) -> bool:
                    if (
                        type(node) == Comparison
                        and len(node.comparisons) == 1
                        and type(node.comparisons[0].operator) == Is
                        and (
                            type(node.left) == Integer
                            or (
                                type(node.left) == Tuple
                                and len(node.left.elements) == 0
                            )
                            or type(node.comparisons[0].comparator) == Integer
                            or (
                                type(node.comparisons[0].comparator) == Tuple
                                and len(node.comparisons[0].comparator.elements)
                                == 0
                            )
                        )
                    ):
                        self.is_literal_found = True
                    return not self.is_literal_found

                def on_leave(self, original_node: CSTNode) -> None:
                    pass

                def on_visit_attribute(
                    self, node: CSTNode, attribute: str
                ) -> None:
                    pass

                def on_leave_attribute(
                    self, original_node: CSTNode, attribute: str
                ) -> None:
                    pass

            def predicate(self, tree: CSTNode) -> bool:
                visitor = self.InternalVisitor()
                tree.visit(visitor)
                return visitor.is_literal_found

    class Without:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return IsLiteral.rule not in rules

        class DeleteIsOpFromGrammarChecker(_Base):
            @property
            def identifier(self) -> str:
                return "-il"

            def start_generation(self, generator: Generator) -> None:
                rule = generator.grammar["base_expression"]
                if (
                    rule is None
                    or type(rule) != Alternatives
                    or "is_op" not in rule.alts
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of base_expression GenNode"
                    )
                del rule.alts["is_op"]

        class ChangeGrammarForIsOpChecker(_Base):
            @property
            def identifier(self) -> str:
                return "-il-ch"

            def start_generation(self, generator: Generator) -> None:
                io_rule = generator.grammar["is_op"]
                if (
                    io_rule is None
                    or type(io_rule) != Constructor
                    or io_rule.init != Comparison
                    or "left" not in io_rule.kwargs
                    or type(io_rule.kwargs["left"]) != LambdaConst
                    or io_rule.kwargs["left"].init != GenNode
                    or len(io_rule.kwargs["left"].args) != 1
                    or io_rule.kwargs["left"].args[0] != "base_expression"
                    or "comparisons" not in io_rule.kwargs
                    or type(io_rule.kwargs["comparisons"]) != ListDescriptor
                    or type(io_rule.kwargs["comparisons"].size) != LambdaConst
                    or io_rule.kwargs["comparisons"].size.init != 1
                    or type(io_rule.kwargs["comparisons"].elem) != LambdaConst
                    or type(io_rule.kwargs["comparisons"].elem.init)
                    != Constructor
                    or len(io_rule.kwargs["comparisons"].elem.args) != 0
                    or len(io_rule.kwargs["comparisons"].elem.kwargs) != 0
                    or io_rule.kwargs["comparisons"].elem.init.init
                    != ComparisonTarget
                    or "operator"
                    not in io_rule.kwargs["comparisons"].elem.init.kwargs
                    or type(
                        io_rule.kwargs["comparisons"].elem.init.kwargs[
                            "operator"
                        ]
                    )
                    != LambdaConst
                    or io_rule.kwargs["comparisons"]
                    .elem.init.kwargs["operator"]
                    .init
                    != Is
                    or "comparator"
                    not in io_rule.kwargs["comparisons"].elem.init.kwargs
                    or type(
                        io_rule.kwargs["comparisons"].elem.init.kwargs[
                            "comparator"
                        ]
                    )
                    != LambdaConst
                    or io_rule.kwargs["comparisons"]
                    .elem.init.kwargs["comparator"]
                    .init
                    != GenNode
                    or len(
                        io_rule.kwargs["comparisons"]
                        .elem.init.kwargs["comparator"]
                        .args
                    )
                    != 1
                    or io_rule.kwargs["comparisons"]
                    .elem.init.kwargs["comparator"]
                    .args[0]
                    != "base_expression"
                    or "lpar" not in io_rule.kwargs
                    or "rpar" not in io_rule.kwargs
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of is_op GenNode"
                    )
                generator.grammar["is_op"] = Constructor(
                    Comparison,
                    left=LambdaConst(GenNode, "il_cgfio__not_int_expression"),
                    comparisons=ListDescriptor(
                        LambdaConst(1),
                        LambdaConst(
                            Constructor(
                                ComparisonTarget,
                                operator=LambdaConst(Is),
                                comparator=LambdaConst(
                                    GenNode, "il_cgfio__not_int_expression"
                                ),
                            )
                        ),
                    ),
                    lpar=io_rule.kwargs["lpar"],
                    rpar=io_rule.kwargs["rpar"],
                )
                be_rule = generator.grammar["base_expression"]
                if be_rule is None or type(be_rule) != Alternatives:
                    raise UnexpectedFailure(
                        "Unexpected structure of base_expression GenNode"
                    )
                generator.grammar["il_cgfio__not_int_expression"] = (
                    Alternatives(
                        {
                            tag: be_rule.alts[tag]
                            for tag in filter(
                                lambda tag: tag != "integer" and tag != "tuple",
                                be_rule.alts,
                            )
                        }
                    )
                )
