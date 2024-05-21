from .if_tuple_checker import IfTuple
from .is_literal_checker import IsLiteral
from .unused_variable_checker import UnusedVariable
from .undefined_name_checker import UndefinedName
from .module_node import ModuleInnerVersion

from framework import *

import sys
from keyword import kwlist


class SimpleGenerator:
    @staticmethod
    def get_grammar() -> Grammar:
        return Grammar(
            "simple",
            "module",
            Constructor(
                ModuleInnerVersion,
                functions=ListDescriptor(
                    lambda choose: choose.F_hat(3, 3, 1.2),
                    LambdaConst(LambdaConst, GenNode, "function_def"),
                ),
                main_block=LambdaConst(GenNode, "main_block"),
            ),
            "main_block",
            LambdaConst(
                GenNode,
                "indented_block",
            ),
            "function_def",
            Constructor(
                FunctionDef,
                name=LambdaConst(GenNode, "new_name"),
                params=LambdaConst(GenNode, "parameters"),
                body=LambdaConst(GenNode, "indented_block"),
            ),
            "parameters",
            Constructor(
                Parameters,
                params=ListDescriptor(
                    lambda choose: choose.F_hat(2, 2, 1),
                    LambdaConst(
                        Constructor,
                        Param,
                        name=LambdaConst(GenNode, "new_name"),
                    ),
                ),
            ),
            "indented_block",
            Constructor(
                IndentedBlock,
                body=ListDescriptor(
                    lambda choose: choose.F_hat(8, 7, 1.5),
                    LambdaConst(LambdaConst, GenNode, "statement_line"),
                ),
            ),
            "statement_line",
            Alternatives(
                {
                    "assign_line": [100, LambdaConst(GenNode, "assign_line")],
                    "if_block": [30, LambdaConst(GenNode, "if_block")],
                    "while_block": [15, LambdaConst(GenNode, "while_block")],
                }
            ),
            "return_line",
            LambdaConst(
                SimpleStatementLine, [Return(GenNode("base_expression"))]
            ),
            "assign_line",
            LambdaConst(
                SimpleStatementLine,
                [
                    Assign(
                        [GenNode("assign_target")], GenNode("base_expression")
                    )
                ],
            ),
            "assign_target",
            Constructor(
                AssignTarget,
                target=LambdaConst(GenNode, "new_name"),
            ),
            "if_block",
            Constructor(
                If,
                test=LambdaConst(GenNode, "base_expression"),
                body=LambdaConst(GenNode, "indented_block"),
            ),
            "while_block",
            Constructor(
                While,
                test=LambdaConst(GenNode, "base_expression"),
                body=LambdaConst(GenNode, "indented_block"),
            ),
            "base_expression",
            Alternatives(
                {
                    "object_or_method": [
                        100,
                        LambdaConst(GenNode, "object_or_method"),
                    ],
                    "integer": [100, LambdaConst(GenNode, "integer")],
                    "tuple": [20, LambdaConst(GenNode, "tuple")],
                    "is_op": [15, LambdaConst(GenNode, "is_op")],
                    "eq_op": [15, LambdaConst(GenNode, "eq_op")],
                }
            ),
            "object_or_method",
            Alternatives(
                {
                    "object": LambdaConst(GenNode, "new_name"),
                }
            ),
            "tuple",
            Constructor(
                Tuple,
                elements=ListDescriptor(
                    lambda choose: choose.N(5),
                    LambdaConst(
                        Constructor,
                        Element,
                        LambdaConst(GenNode, "base_expression"),
                    ),
                ),
            ),
            "is_op",
            Constructor(
                Comparison,
                left=LambdaConst(GenNode, "base_expression"),
                comparisons=ListDescriptor(
                    LambdaConst(1),
                    LambdaConst(
                        Constructor(
                            ComparisonTarget,
                            operator=LambdaConst(Is),
                            comparator=LambdaConst(GenNode, "base_expression"),
                        )
                    ),
                ),
                lpar=ListDescriptor(
                    LambdaConst(1), LambdaConst(Constructor, LeftParen)
                ),
                rpar=ListDescriptor(
                    LambdaConst(1), LambdaConst(Constructor, RightParen)
                ),
            ),
            "eq_op",
            Constructor(
                Comparison,
                left=LambdaConst(GenNode, "base_expression"),
                comparisons=ListDescriptor(
                    LambdaConst(1),
                    LambdaConst(
                        Constructor(
                            ComparisonTarget,
                            operator=LambdaConst(Equal),
                            comparator=LambdaConst(GenNode, "base_expression"),
                        )
                    ),
                ),
                lpar=ListDescriptor(
                    LambdaConst(1), LambdaConst(Constructor, LeftParen)
                ),
                rpar=ListDescriptor(
                    LambdaConst(1), LambdaConst(Constructor, RightParen)
                ),
            ),
            "new_name",
            Constructor(
                Name,
                value=Filter(
                    lambda name: name not in kwlist and name != "_",
                    Constructor(
                        lambda raw_name: "".join(raw_name),
                        ListDescriptor(
                            lambda choose: choose.N(10) + 1,
                            lambda index, _: Alternatives(
                                [
                                    Constructor(lambda c=c: c)
                                    for c in (
                                        "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_"
                                        + ("1234567890" if index != 0 else "")
                                    )
                                ]
                            ),
                        ),
                    ),
                ),
            ),
            "integer",
            Constructor(
                lambda sign_fun, nat: (
                    sign_fun(Integer(nat)) if nat != "" else Integer("0")
                ),
                sign_fun=Alternatives(
                    [
                        LambdaConst(lambda: (lambda i: i)),
                        LambdaConst(
                            lambda: (lambda i: UnaryOperation(Minus(), i))
                        ),
                    ]
                ),
                nat=Constructor(
                    lambda raw: "".join(raw),
                    raw=ListDescriptor(
                        lambda choose: choose.N(7),
                        lambda index, _: Alternatives(
                            [
                                Constructor(lambda c=c: c)
                                for c in (
                                    "123456789" + ("0" if index != 0 else "")
                                )
                            ]
                        ),
                    ),
                ),
            ),
        )

    @staticmethod
    def get_tree_depth_checker() -> TreeDepthChecker:
        return TreeDepthChecker(
            {"statement_line": {"if_block": 1, "while_block": 1}}, 3, ""
        )

    @staticmethod
    def get_checkers() -> dict[str, RuleChecker]:
        return dict(
            map(
                lambda c: (c.identifier, c),
                [
                    UnusedVariable.With.AddAssignInFirstLineOfMainBlockChecker(),
                    UnusedVariable.With.ContainsPredicateChecker(),
                    UnusedVariable.Without.AddTupleInLastLineOfBlockChecker(),
                    UndefinedName.With.ContainsPredicateChecker(),
                    UndefinedName.Without.NotNewNameInObjectOrMethodChecker(),
                    IfTuple.With.MaybeIfBlockAtTheEndChecker(),
                    IfTuple.With.ContainsPredicateChecker(),
                    IfTuple.Without.DeleteTupleFromGrammarChecker(),
                    IfTuple.Without.ChangeGrammarForIfChecker(),
                    IfTuple.Without.DeleteIfWithTupleChecker(),
                    IsLiteral.With.ContainsPredicateChecker(),
                    IsLiteral.Without.DeleteIsOpFromGrammarChecker(),
                    IsLiteral.Without.ChangeGrammarForIsOpChecker(),
                ],
            )
        )

    @classmethod
    def FromArgs(cls, seed: int, args: list[str]) -> Generator:
        return Generator(
            seed,
            cls.get_grammar(),
            [cls.get_tree_depth_checker()]
            + list(map(cls.get_checkers().__getitem__, args)),
        )
