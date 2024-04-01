from dataclasses import dataclass
from libcst import CSTNode, FunctionDef, IndentedBlock, CSTVisitorT
from libcst._nodes.internal import CodegenState, visit_body_sequence, visit_required


@dataclass(frozen=True)
class ModuleInnerVersion(CSTNode):
    functions: list[FunctionDef]
    main_block: IndentedBlock

    def _visit_and_replace_children(self, visitor: CSTVisitorT) -> "ModuleInnerVersion":
        return ModuleInnerVersion(
            functions=visit_body_sequence(self, "functions", self.functions, visitor),
            main_block=visit_required(self, "main_block", self.main_block, visitor),
        )

    def _codegen_impl(self, state: CodegenState) -> None:
        for func in self.functions:
            func._codegen(state)
        for line in self.main_block.body:
            line._codegen(state)

    @property
    def code(self) -> str:
        state = CodegenState(default_indent=" " * 4, default_newline="\n")
        self._codegen(state)
        return "".join(state.tokens)
