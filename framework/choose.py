from .failures import AllowableFailure

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Tuple
import random


@dataclass(frozen=True)
class Choose:
    seed: int

    def __post_init__(self):
        random.seed(self.seed)

    def N(self, n: int) -> int:
        if n <= 0:
            raise AllowableFailure()
        return random.randrange(n)

    def B(self, p: float) -> bool:
        N = 100
        pN = round(N * p)
        return self.N(N) < pN

    def RP(self, rps: Iterable[int]) -> int:
        nrps = map(lambda x: max(0, x), rps)
        lrps = list(nrps) if type(rps) is not list else nrps
        n = self.N(sum(lrps))
        for i, rp in enumerate(lrps):
            if rp <= n:
                n -= rp
            else:
                return i

    def F(self, p: Callable[int, int], first: int, last: int) -> int:
        return self.RP(map(p, range(first, last + 1))) + first

    def L(self, xs: Iterable[Any]) -> Any:
        lxs = list(xs) if type(xs) is not list else xs
        i = self.N(len(lxs))
        return lxs[i]

    def LRP(self, pxs: Iterable[Tuple[int, Any]]) -> Any:
        lpxs = list(pxs) if type(pxs) is not list else pxs
        i = self.RP(map(lambda x: x[0], lpxs))
        return lpxs[i][1]

    def F_hat(self, average: int, variance: int, privilege: float) -> int:
        N = 100
        privilegeN = round(N * privilege)
        return self.F(
            lambda x: privilegeN
            - (privilegeN - N) * abs(x - average) // variance,
            average - variance,
            average + variance,
        )

    def N_many(self, n: int, m: int) -> list[int]:
        a = list(range(n))
        for i in range(m):
            j = self.N(n - i)
            a[i], a[j] = a[j], a[i]
        return a[:m]
