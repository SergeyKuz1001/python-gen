from framework import *

from typing import Optional, Callable


class UnusedVariable:
    rule: str = "F841"

    class Without:
        class AddTupleInLastLineOfBlockChecker(ScopeChecker, RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return UnusedVariable.rule not in rules

            @property
            def identifier(self) -> str:
                return "-uv"

            def start_generation(self, generator: Generator) -> None:
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
                        lambda choose: rule.kwargs["body"].size(choose)
                        + 1,
                        lambda index, length: (
                            rule.kwargs["body"].elem(index, length - 1)
                            if index + 1 != length
                            else LambdaConst(GenNode, "uv_atillob__tuple")
                        ),
                    ),
                )
                generator.grammar["uv_atillob__tuple"] = GenGetter(
                    lambda generator: LambdaConst(
                        SimpleStatementLine,
                        [
                            Expr(
                                Tuple(
                                    [
                                        Element(Name(var))
                                        for var, _ in filter(
                                            lambda p: not p[1],
                                            generator.find_checker(
                                                type(self)
                                            ).last.items(),
                                        )
                                    ]
                                )
                            )
                        ],
                    )
                )

            def leave_pure_node(self, node: CSTNode, generator: Generator) -> None:
                if generator.on_trace(
                    SearchThroughMany("base_expression", Any()), Name
                ):
                    if node.value in map(lambda p: p[0], self):
                        self[node.value] %= lambda _: True
                elif (
                    generator.on_trace(SimpleStatementLine, Assign)
                    and type(node.targets[0].target) == Name
                ):
                    self[node.targets[0].target.value] = False
                elif generator.on_trace(FunctionDef):
                    self[node.name.value] = False
                elif generator.on_trace(Param, "new_name", Name):
                    self[node.value] = False
