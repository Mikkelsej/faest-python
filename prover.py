from typing import TYPE_CHECKING
from field import ExtensionField

if TYPE_CHECKING:
    from vole import Vole


class Prover:
    def __init__(self, vole: "Vole") -> None:
        self.vole = vole
        self.field: ExtensionField = vole.field
        self.length: int = vole.length

        self.u: list[int]
        self.v: list[int]

        self.index: int = 0

        vole.initialize_prover(self)

    def set_u(self, u: list[int]) -> None:
        self.u = u

    def set_v(self, v: list[int]) -> None:
        self.v = v

    def commit(self, w: list[int]) -> tuple[int, int]:
        i: int = self.index
        di: int = self.field.add(self.u[i], w[i])

        # Going to next unused ui and wi
        self.index += 1

        return i, di

    def open(self, wi: int, vi: int, index: int) -> tuple[int, int, int]:
        return wi, vi, index

    def add(self, v0: int, v1: int, u0: int, u1: int) -> tuple[int, int]:
        return self.field.add(v0, v1), self.field.add(u0, u1)

    def mul(self, a: int, b: int, c: int) -> tuple[int, int]:

        d: int = self.field.sub(
            self.field.add(
                self.field.mul(self.v[a], self.u[b]),
                self.field.mul(self.v[b], self.u[a]),
            ),
            self.v[c],
        )
        e: int = self.field.mul(self.v[a], self.v[b])

        return d, e

    def mul_commit(self, a: int, b: int):
        c: int = self.index
        self.index += 1

        uc: int = self.field.mul(self.u[a], self.u[b])

        correction: int = self.field.sub(uc, self.u[c])

        self.u[c] = uc

        return c, correction
