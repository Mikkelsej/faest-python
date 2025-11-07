from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vole import Vole


class Verifier:
    def __init__(self, vole: "Vole") -> None:
        self.vole = vole
        self.field = vole.field
        self.delta: int
        self.q: list[int]
        self.index: int = 0
        vole.initialize_verifier(self)

    def set_delta(self, delta: int) -> None:
        self.delta = delta

    def set_q(self, q: list[int]) -> None:
        self.q = q

    def update_q(self, index: int, di: int) -> None:
        i: int = index
        qi: int = self.field.add(self.q[i], self.field.mul(di, self.delta))
        self.q[i] = qi

    def check_open(self, wi: int, vi: int, index: int) -> bool:
        original_qi: int = self.q[index]

        new_qi = self.field.add(vi, self.field.mul(wi, self.delta))

        if original_qi == new_qi:
            return True

        return False

    def add(self, index_a: int, index_b: int) -> int:
        """Add two committed values and return the result index"""
        c = self.index
        self.index += 1

        # q[c] = q[a] + q[b] (addition is linear, no correction needed)
        self.q[c] = self.field.add(self.q[index_a], self.q[index_b])

        return c

    def mul(self, index_a: int, index_b: int, correction: int) -> int:
        """Allocate result index and apply correction for multiplication"""
        c = self.index
        self.index += 1

        # Apply the correction to q[c]
        self.update_q(c, correction)

        return c

    def check_mul(self, index_a: int, index_b: int, index_c: int, d: int, e: int) -> bool:
        delta: int = self.delta

        lhs: int = self.field.sub(
            self.field.mul(self.q[index_a], self.q[index_b]), self.field.mul(delta, self.q[index_c])
        )

        rhs: int = self.field.add(self.field.mul(d, delta), e)

        return lhs == rhs
