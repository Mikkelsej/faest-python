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

    def commit(self, w: int) -> tuple[int, int]:
        """Returns i, di"""
        i: int = self.index
        di: int = self.field.add(self.u[i], w)

        # Going to next unused ui and wi
        self.index += 1

        return i, di

    def open(self, wi: int, vi: int, index: int) -> tuple[int, int, int]:
        return wi, vi, index

    def add(self, a: int, b: int) -> int:
        """Add two committed values and return the result index"""
        c = self.index
        self.index += 1

        self.v[c] = self.field.add(self.v[a], self.v[b])
        self.u[c] = self.field.add(self.u[a], self.u[b])

        return c

    def mul(self, a: int, b: int) -> tuple[int, int, int, int]:
        """Multiply two committed values and return (result_index, correction, d, e)"""
        c = self.index
        self.index += 1

        # Commit u[c] = u[a] * u[b]
        uc = self.field.mul(self.u[a], self.u[b])
        correction = self.field.sub(uc, self.u[c])
        self.u[c] = uc

        # Compute correction values for verification
        d = self.field.sub(
            self.field.add(
                self.field.mul(self.v[a], self.u[b]),
                self.field.mul(self.v[b], self.u[a]),
            ),
            self.v[c],
        )
        e = self.field.mul(self.v[a], self.v[b])

        return c, correction, d, e
