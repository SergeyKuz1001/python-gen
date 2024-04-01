from choose import Choose

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, Union
from libcst import CSTNodeT


class ConfigPart(ABC):
    @abstractmethod
    def generate(self, generator: "Generator") -> any: ...


@dataclass()
class LambdaConst(ConfigPart):
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
class Constructor(ConfigPart):
    init: Callable[["args"], any]
    args: list[ConfigPart] = field(default_factory=list)
    kwargs: dict[str, ConfigPart] = field(default_factory=dict)

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
class ListDescriptor(ConfigPart):
    size: Callable[[Choose], int]
    elem: Union[Callable[[int, int], ConfigPart], LambdaConst]

    def generate(self, generator: "Generator") -> any:
        size = self.size(generator.choose)
        return [self.elem(index, size).generate(generator) for index in range(size)]


@dataclass()
class Alternatives(ConfigPart):
    alts: dict[str, tuple[int, ConfigPart]]

    def __init__(
        self,
        alts: Union[
            list[ConfigPart],
            list[tuple[int, ConfigPart]],
            dict[str, ConfigPart],
            dict[str, tuple[int, ConfigPart]],
        ],
    ):
        if type(alts) == dict:
            if isinstance(list(alts.values())[0], ConfigPart):
                self.alts = {tag: [1, part] for tag, part in alts.items()}
            else:
                self.alts = alts
        else:
            if isinstance(alts[0], ConfigPart):
                self.alts = {idx: [1, part] for idx, part in enumerate(alts)}
            else:
                self.alts = {idx: [w, part] for idx, (w, part) in enumerate(alts)}

    def generate(self, generator: "Generator") -> any:
        return generator.choose.LRP(list(self.alts.values())).generate(generator)


@dataclass()
class Filter(ConfigPart):
    pred: Callable[[any], bool]
    main: ConfigPart

    def generate(self, generator: "Generator") -> any:
        while True:
            result = self.main.generate(generator)
            if self.pred(result):
                return result


@dataclass()
class GenGetter(ConfigPart):
    func: Callable[["Generator"], ConfigPart]

    def generate(self, generator: "Generator") -> any:
        return self.func(generator).generate(generator)


Config = dict[str, ConfigPart]
