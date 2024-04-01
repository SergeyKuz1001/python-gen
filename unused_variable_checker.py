from abstract_scope_checker import AbstractScopeChecker
from rule_checker import RuleChecker
from gen_node import GenNode
from generator import Generator, TL
from config import Constructor, ListDescriptor, LambdaConst, GenGetter
from failures import UnexpectedFailure

from libcst import (
    IndentedBlock,
    CSTNode,
    FunctionDef,
    Assign,
    AssignTarget,
    Name,
    SimpleStatementLine,
    Tuple,
    Expr,
    Element,
)
from typing import Optional, Callable


class UnusedVariable:
    rule: str = "F841"

    class Without:
        class AddTupleInLastLineOfBlockChecker(AbstractScopeChecker, RuleChecker):
            def in_rules(self, rules: list[str], generator: Generator) -> bool:
                return UnusedVariable.rule not in rules

            def start_generation(self, generator: Generator) -> None:
                config_indented_block = generator.config.get("indented_block")
                if (
                    config_indented_block is None
                    or type(config_indented_block) != Constructor
                    or config_indented_block.init != IndentedBlock
                    or "body" not in config_indented_block.kwargs
                    or type(config_indented_block.kwargs["body"]) != ListDescriptor
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of indented_block GenNode"
                    )
                generator.config["indented_block"] = Constructor(
                    IndentedBlock,
                    body=ListDescriptor(
                        lambda choose: config_indented_block.kwargs["body"].size(choose)
                        + 1,
                        lambda index, length: (
                            config_indented_block.kwargs["body"].elem(index, length - 1)
                            if index + 1 != length
                            else LambdaConst(GenNode, "uv_atillob__tuple")
                        ),
                    ),
                )
                generator.config["uv_atillob__tuple"] = GenGetter(
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
                    TL.SearchThroughMany("base_expression", TL.Any()), Name
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
