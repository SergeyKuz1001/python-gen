from .generator import Generator
from .adapters import AbstractAdapter

from dataclasses import dataclass
from os import path, makedirs


@dataclass(frozen=True)
class Tester:
    generator: Generator
    adapter: AbstractAdapter
    cache_dir: str

    @property
    def codefilename(self) -> str:
        if not hasattr(self, "_codefilename"):
            object.__setattr__(
                self,
                "_codefilename",
                path.join(self.cache_dir, self.generator.identifier + ".py"),
            )
        return self._codefilename

    @property
    def statfilename(self) -> str:
        if not hasattr(self, "_statfilename"):
            object.__setattr__(
                self,
                "_statfilename",
                path.join(
                    self.cache_dir,
                    self.generator.identifier
                    + "."
                    + self.adapter.identifier
                    + "-accepted",
                ),
            )
        return self._statfilename

    def generate_code(self) -> bool:
        if path.isfile(self.codefilename):
            return False
        else:
            if not path.isdir(self.cache_dir):
                makedirs(self.cache_dir)
            with open(self.codefilename, "w") as fout:
                print(self.generator.code, file=fout)
            return True

    def test_linter(self) -> bool:
        if path.isfile(self.statfilename):
            return True
        else:
            self.generate_code()
            rules = self.adapter.get_rules(self.codefilename)
            for rule_checker in self.generator.rule_checkers:
                if not rule_checker.in_rules(rules):
                    print(
                        f"Rules match failure for checker {rule_checker.identifier}, rules = {rules}"
                    )
                    return False
            with open(self.statfilename, "w") as fout:
                print("", end="", file=fout)
            return True
