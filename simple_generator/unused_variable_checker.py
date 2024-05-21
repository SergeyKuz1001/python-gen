from .module_node import ModuleInnerVersion

from framework import *

from typing import Optional, Callable


class UnusedVariable:
    rule: str = "F841"

    class With:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return UnusedVariable.rule in rules

        class AddAssignInFirstLineOfMainBlockChecker(_Base):
            @property
            def identifier(self) -> str:
                return "+uv-sa"

            def start_generation(self, generator: Generator) -> None:
                mm_rule = generator.grammar["module"]
                if (
                    mm_rule is None
                    or type(mm_rule) != Constructor
                    or mm_rule.init != ModuleInnerVersion
                    or "functions" not in mm_rule.kwargs
                    or type(mm_rule.kwargs["functions"]) != ListDescriptor
                    or "main_block" not in mm_rule.kwargs
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of module GenNode"
                    )
                generator.grammar["module"] = Constructor(
                    ModuleInnerVersion,
                    functions=ListDescriptor(
                        lambda choose: mm_rule.kwargs["functions"].size(choose)
                        + 1,
                        mm_rule.kwargs["functions"].elem,
                    ),
                    main_block=mm_rule.kwargs["main_block"],
                )
                ib_rule = generator.grammar["indented_block"]
                if (
                    ib_rule is None
                    or type(ib_rule) != Constructor
                    or ib_rule.init != IndentedBlock
                    or "body" not in ib_rule.kwargs
                    or type(ib_rule.kwargs["body"]) != ListDescriptor
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of indented_block GenNode"
                    )
                generator.grammar["indented_block"] = Constructor(
                    IndentedBlock,
                    body=ListDescriptor(
                        lambda choose: ib_rule.kwargs["body"].size(choose) + 1,
                        lambda index, length: (
                            ib_rule.kwargs["body"].elem(index - 1, length - 1)
                            if index != 0
                            else LambdaConst(
                                SimpleStatementLine,
                                [
                                    Assign(
                                        [AssignTarget(Name("a" * 11))],
                                        Integer("0"),
                                    )
                                ],
                            )
                        ),
                    ),
                )

        class ContainsPredicateChecker(_Base, PredicateChecker):
            @property
            def identifier(self) -> str:
                return "+uv"

            class InternalVisitor(CSTVisitor):
                def __init__(self):
                    self.name_in_left_side: bool = False
                    self.in_function_body: bool = False
                    self.unused_names: set[str] = set()

                def visit_FunctionDef_body(self, node: "FunctionDef") -> None:
                    self.in_function_body = True

                def leave_FunctionDef_body(self, node: "FunctionDef") -> None:
                    self.in_function_body = False

                def visit_AssignTarget_target(
                    self, node: "AssignTarget"
                ) -> None:
                    self.name_in_left_side = True

                def leave_AssignTarget_target(
                    self, node: "AssignTarget"
                ) -> None:
                    self.name_in_left_side = False

                def visit_Name(self, node: "Name") -> bool:
                    if self.name_in_left_side and self.in_function_body:
                        self.unused_names.add(node.value)
                    else:
                        if node.value in self.unused_names:
                            self.unused_names.remove(node.value)

            def predicate(self, tree: CSTNode) -> bool:
                visitor = self.InternalVisitor()
                tree.visit(visitor)
                return len(visitor.unused_names) != 0

    class Without:
        class _Base(RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return UnusedVariable.rule not in rules

        class AddTupleInLastLineOfBlockChecker(_Base, ScopeChecker):
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
                        lambda choose: rule.kwargs["body"].size(choose) + 1,
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

            def leave_pure_node(
                self, node: CSTNode, generator: Generator
            ) -> None:
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
