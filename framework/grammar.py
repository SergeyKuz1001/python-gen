from .gen_node import GenNode

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, Union
from libcst import CSTNode


class RuleBody(ABC):
    @abstractmethod
    def generate(self, generator: "Generator") -> any: ...


@dataclass()
class LambdaConst(RuleBody):
    init: Callable[["args"], any]
    args: list[any] = field(default_factory=list)
    kwargs: dict[str, any] = field(default_factory=dict)

    def __init__(self, init: Callable[["args"], any], *args, **kwargs):
        self.init = init
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> any:
        return self.init(*(self.args), **(self.kwargs))

    def generate(self, generator: "Generator") -> any:
        return self.__call__()


@dataclass()
class Constructor(RuleBody):
    init: Callable[["args"], any]
    args: list[RuleBody] = field(default_factory=list)
    kwargs: dict[str, RuleBody] = field(default_factory=dict)

    def __init__(
        self, init: Union[Callable[["args"], any], LambdaConst], *args, **kwargs
    ):
        self.init = init
        self.args = args
        self.kwargs = kwargs

    def generate(self, generator: "Generator") -> any:
        return self.init(
            *[part.generate(generator) for part in self.args],
            **{name: part.generate(generator) for name, part in self.kwargs.items()}
        )


@dataclass()
class ListDescriptor(RuleBody):
    size: Callable[["Choose"], int]
    elem: Union[Callable[[int, int], RuleBody], LambdaConst]

    def generate(self, generator: "Generator") -> any:
        size = self.size(generator.choose)
        return [self.elem(index, size).generate(generator) for index in range(size)]


@dataclass()
class Alternatives(RuleBody):
    alts: dict[str, tuple[int, RuleBody]]

    def __init__(
        self,
        alts: Union[
            list[RuleBody],
            list[tuple[int, RuleBody]],
            dict[str, RuleBody],
            dict[str, tuple[int, RuleBody]],
        ],
    ):
        if type(alts) == dict:
            if isinstance(list(alts.values())[0], RuleBody):
                self.alts = {tag: [1, part] for tag, part in alts.items()}
            else:
                self.alts = alts
        else:
            if isinstance(alts[0], RuleBody):
                self.alts = {idx: [1, part] for idx, part in enumerate(alts)}
            else:
                self.alts = {idx: [w, part] for idx, (w, part) in enumerate(alts)}

    def generate(self, generator: "Generator") -> any:
        return generator.choose.LRP(list(self.alts.values())).generate(generator)


@dataclass()
class Filter(RuleBody):
    pred: Callable[[any], bool]
    main: RuleBody

    def generate(self, generator: "Generator") -> any:
        while True:
            result = self.main.generate(generator)
            if self.pred(result):
                return result


@dataclass()
class GenGetter(RuleBody):
    func: Callable[["Generator"], RuleBody]

    def generate(self, generator: "Generator") -> any:
        return self.func(generator).generate(generator)


class Grammar:
    def __init__(self, identifier: str, start_tag: str, start_body: RuleBody, *rules):
        self._identifier = identifier
        self._start = GenNode(start_tag)
        self._rules = {start_tag: [start_body]}
        for tag, body in zip(rules[0::2], rules[1::2]):
            self._rules[tag] = [body]

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def start(self) -> GenNode:
        return self._start

    def generate(self, node: GenNode, generator: "Generator") -> CSTNode:
        return self[node.tag].generate(generator)

    def __contains__(self, tag: str) -> bool:
        return tag in self._rules

    def __getitem__(self, tag: str) -> Optional[RuleBody]:
        if tag not in self or len(self._rules[tag]) == 0:
            return None
        return self._rules[tag][-1]

    def __setitem__(self, tag: str, body: RuleBody) -> None:
        if tag not in self:
            self._rules[tag] = []
        self._rules[tag].append(body)

    def __delitem__(self, tag: str) -> None:
        self._rules[tag].pop()
