from .failures import UnexpectedFailure

from dataclasses import dataclass
from libcst import CSTNode, CSTVisitorT


@dataclass(frozen=True)
class GenNode(CSTNode):
    tag: str

    def generate(self, generator: "Generator") -> CSTNode:
        return generator.grammar.generate(self, generator)

    def _visit_and_replace_children(self, visitor: CSTVisitorT) -> CSTNode:
        raise UnexpectedFailure(
            "Can't call method _visit_and_replace_children for GenNode"
        )

    def _codegen_impl(self, state: "CodegenState") -> None:
        state.add_token(f"\033[33m<{self.tag}>\033[0m")
