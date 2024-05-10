from framework import *

from typing import Optional, Callable


class UndefinedName:
    rule: str = "F821"

    class Without:
        class NotNewNameInObjectOrMethodChecker(ScopeChecker, RuleChecker):
            def in_rules(self, rules: list[str]) -> bool:
                return UndefinedName.rule not in rules

            @property
            def identifier(self) -> str:
                return "-un"

            def start_generation(self, generator: Generator) -> None:
                rule = generator.grammar["object_or_method"]
                if (
                    rule is None
                    or type(rule) != Alternatives
                    or type(rule.alts) != dict
                    or "object" not in rule.alts
                ):
                    raise UnexpectedFailure(
                        "Unexpected structure of object_or_method GenNode"
                    )
                generator.grammar["object_or_method"] = Alternatives(
                    {
                        tag: (
                            part
                            if tag != "object"
                            else LambdaConst(GenNode, "un_nnnioom__object")
                        )
                        for tag, part in rule.alts.items()
                    }
                )
                generator.grammar["un_nnnioom__object"] = GenGetter(
                    lambda generator: Alternatives(
                        [
                            Constructor(lambda var=var: Name(var))
                            for var, _ in generator.find_checker(type(self))
                        ]
                    )
                )

            def revisit_mid_node(
                self, mid_node: CSTNode, new_node: Optional[CSTNode], generator: Generator
            ) -> None:
                super().revisit_mid_node(mid_node, new_node, generator)
                if new_node is None and generator.on_trace("module"):
                    for name in ("True", "False", "None"):
                        self[name] = ()

            def leave_gen_node(
                self, node: GenNode, new_node: CSTNode, generator: Generator
            ) -> None:
                if generator.on_trace("assign_line"):
                    self[new_node.body[0].targets[0].target.value] = ()
                elif generator.on_trace("parameters"):
                    for param in new_node.params:
                        self[param.name.value] = ()
                elif generator.on_trace("function_def"):
                    self[new_node.name.value] = ()
