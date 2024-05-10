from .if_tuple_checker import IfTuple
from .unused_variable_checker import UnusedVariable
from .undefined_name_checker import UndefinedName
from .module_node import ModuleInnerVersion

from framework import *

import sys
from keyword import kwlist


class SimpleGenerator:
    @staticmethod
    def FromArgs(seed: int, args: list[str]) -> Generator:
        g = Grammar("simple",
            "module", Constructor(
                ModuleInnerVersion,
                functions=ListDescriptor(
                    lambda choose: choose.F_hat(3, 3, 1.2),
                    LambdaConst(LambdaConst, GenNode, "function_def"),
                ),
                main_block=LambdaConst(GenNode, "indented_block"),
            ),
            "function_def", Constructor(
                FunctionDef,
                name=LambdaConst(GenNode, "new_name"),
                params=LambdaConst(GenNode, "parameters"),
                body=LambdaConst(GenNode, "indented_block"),
            ),
            "parameters", Constructor(
                Parameters,
                params=ListDescriptor(
                    lambda choose: choose.F_hat(2, 2, 1),
                    LambdaConst(Constructor, Param, name=LambdaConst(GenNode, "new_name")),
                ),
            ),
            "indented_block", Constructor(
                IndentedBlock,
                body=ListDescriptor(
                    lambda choose: choose.F_hat(8, 7, 1.5),
                    LambdaConst(LambdaConst, GenNode, "statement_line"),
                ),
            ),
            "statement_line", Alternatives(
                {
                    "assign_line": [100, LambdaConst(GenNode, "assign_line")],
                    "if_block": [25, LambdaConst(GenNode, "if_block")],
                }
            ),
            "return_line", LambdaConst(
                SimpleStatementLine, [Return(GenNode("base_expression"))]
            ),
            "assign_line", LambdaConst(
                SimpleStatementLine,
                [Assign([GenNode("assign_target")], GenNode("base_expression"))],
            ),
            "assign_target", Constructor(
                AssignTarget,
                target=LambdaConst(GenNode, "new_name"),
            ),
            "if_block", Constructor(
                If,
                test=LambdaConst(GenNode, "base_expression"),
                body=LambdaConst(GenNode, "indented_block"),
            ),
            "base_expression", Alternatives(
                {
                    "object_or_method": [100, LambdaConst(GenNode, "object_or_method")],
                    "integer": [50, LambdaConst(GenNode, "integer")],
                    "tuple": [25, LambdaConst(GenNode, "tuple")],
                }
            ),
            "object_or_method", Alternatives(
                {
                    "object": LambdaConst(GenNode, "new_name"),
                }
            ),
            "tuple", Constructor(
                Tuple,
                elements=ListDescriptor(
                    lambda choose: choose.N(5),
                    LambdaConst(
                        Constructor, Element, LambdaConst(GenNode, "base_expression")
                    ),
                ),
            ),
            "new_name", Constructor(
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
            "integer", Constructor(
                lambda sign_fun, nat: sign_fun(Integer(nat)) if nat != "" else Integer("0"),
                sign_fun=Alternatives(
                    [
                        LambdaConst(lambda: (lambda i: i)),
                        LambdaConst(lambda: (lambda i: UnaryOperation(Minus(), i))),
                    ]
                ),
                nat=Constructor(
                    lambda raw: "".join(raw),
                    raw=ListDescriptor(
                        lambda choose: choose.N(7),
                        lambda index, _: Alternatives(
                            [
                                Constructor(lambda c=c: c)
                                for c in ("123456789" + ("0" if index != 0 else ""))
                            ]
                        ),
                    ),
                ),
            ),
        )
        cs = [TreeDepthChecker({"statement_line": {"if_block": 1}}, 3)]
        cs[0].identifier = ""
        for arg in args:
            if arg in ("-unused_variable", "-uv", "-F481"):
                cs.append(UnusedVariable.Without.AddTupleInLastLineOfBlockChecker())
            elif arg in ("-undefined_name", "-un", "-F421"):
                cs.append(UndefinedName.Without.NotNewNameInObjectOrMethodChecker())
            elif arg in ("+if_tuple", "+it", "+F634"):
                cs.append(IfTuple.With.MaybeIfBlockAtTheEndChecker())
            elif arg in ("-if_tuple", "-it", "-F634"):
                cs.append(IfTuple.Without.DeleteTupleFromConfigChecker())
        return Generator(seed, g, cs)
