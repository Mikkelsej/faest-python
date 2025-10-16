from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vole import Vole


class Verifier:
    def __init__(self, vole: "Vole") -> None:
        self.vole = vole
        self.field = vole.field
        self.delta: int
        self.q: list[int]
        vole.initializeVerifier(self)

    def setDelta(self, delta: int) -> None:
        self.delta = delta

    def setQ(self, q: list[int]) -> None:
        self.q = q

    def updateQ(self, index: int, di: int):
        i: int = index
        qi: int = self.field.add(self.q[i], self.field.mul(di, self.delta))
        self.q[i] = qi

    def check(self, wi: int, vi: int, index: int) -> bool:
        original_qi: int = self.q[index]

        new_qi = self.field.add(vi, self.field.mul(wi, self.delta))

        if original_qi == new_qi:
            return True

        return False

    def add(self, q0: int, q1: int):
        return self.field.add(q0, q1)

    def check_mul(self, q0: int, q1: int, q2: int, d: int, e: int):
        delta: int = self.delta

        lhs: int = self.field.sub(self.field.mul(q0, q1), self.field.mul(delta, q2))

        rhs: int = self.field.add(self.field.mul(d, delta), e)

        return lhs == rhs
