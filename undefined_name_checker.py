from abstract_scope_checker import AbstractScopeChecker
from rule_checker import RuleChecker
from gen_node import GenNode
from generator import Generator
from config import Constructor, Alternatives, ListDescriptor, LambdaConst, GenGetter

from libcst import (
    IndentedBlock,
    CSTNode,
    AssignTarget,
    Name,
    SimpleStatementLine,
    Tuple,
    Expr,
    Element,
)
from typing import Optional, Callable


class UndefinedName:
    rule: str = "F821"

    class Without:
        class NotNewNameInObjectOrMethodChecker(AbstractScopeChecker, RuleChecker):
            def in_rules(self, rules: list[str], generator: Generator) -> bool:
                return UndefinedName.rule not in rules

            def start_generation(self, generator: Generator) -> None:
                config_object_or_method = generator.config.get("object_or_method")
                if (
                    config_object_or_method is None
                    or type(config_object_or_method) != Alternatives
                    or type(config_object_or_method.alts) != dict
                    or "object" not in config_object_or_method.alts
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of object_or_method GenNode"
                    )
                generator.config["object_or_method"] = Alternatives(
                    {
                        tag: (
                            part
                            if tag != "object"
                            else LambdaConst(GenNode, "un_nnnioom__object")
                        )
                        for tag, part in config_object_or_method.alts.items()
                    }
                )
                generator.config["un_nnnioom__object"] = GenGetter(
                    lambda generator: Alternatives(
                        [
                            Constructor(lambda var=var: Name(var))
                            for var, _ in generator.find_checker(type(self))
                        ]
                    )
                )

            def revisit_mid_node(
                self, node: CSTNode, generator: Generator, *args
            ) -> None:
                super().revisit_mid_node(node, generator, *args)
                if len(args) == 0 and generator.on_trace("module"):
                    for name in ("True", "False", "None"):
                        self[name] = ()

            def leave_gen_node(
                self, node: GenNode, new_node: CSTNode, generator: Generator
            ) -> None:
                if generator.on_trace("assign_line"):
                    self[new_node.body[0].targets[0].target.value] = ()
