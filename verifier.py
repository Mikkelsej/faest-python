from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vole import Vole


class Verifier:
    def __init__(self, vole: "Vole") -> None:
        self.vole = vole
        self.field = vole.field
        self.delta: int
        self.q: list[int]
        vole.initialize_verifier(self)

    def set_delta(self, delta: int) -> None:
        self.delta = delta

    def set_q(self, q: list[int]) -> None:
        self.q = q

    def update_q(self, index: int, di: int) -> None:
        i: int = index
        qi: int = self.field.add(self.q[i], self.field.mul(di, self.delta))
        self.q[i] = qi

    def check(self, wi: int, vi: int, index: int) -> bool:
        original_qi: int = self.q[index]

        new_qi = self.field.add(vi, self.field.mul(wi, self.delta))

        if original_qi == new_qi:
            return True

        return False

    def add(self, a: int, b: int) -> int:
        return self.field.add(self.q[a], self.q[b])

    def check_mul(self, a: int, b: int, c: int, d: int, e: int) -> bool:
        delta: int = self.delta

        lhs: int = self.field.sub(
            self.field.mul(self.q[a], self.q[b]), self.field.mul(delta, self.q[c])
        )

        rhs: int = self.field.add(self.field.mul(d, delta), e)

        return lhs == rhs
