from .root_generated_tree import RootGeneratedTreeChecker

from ..failures import AllowableFailure

from abc import ABC, abstractmethod
from libcst import CSTNode


class PredicateChecker(RootGeneratedTreeChecker, ABC):
    @abstractmethod
    def predicate(self, tree: CSTNode) -> bool: ...

    def leave_root(self, root: CSTNode, generator: "Generator") -> None:
        if not self.predicate(root):
            raise AllowableFailure()
