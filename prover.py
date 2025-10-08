
from typing import TYPE_CHECKING
from field import ExtensionField

if TYPE_CHECKING:
    from vole import Vole


class Prover:
    def __init__(self, vole: 'Vole') -> None:
        self.vole = vole
        self.field: ExtensionField = vole.field
        self.length: int = vole.length

        self.u: list[int]
        self.v: list[int]

        self.index: int = 0

        vole.initializeProver(self)

    def setU(self, u: list[int]) -> None:
        self.u = u

    def setV(self, v: list[int]) -> None:
        self.v = v

    def commit(self, w: list[int]) -> int:
        i: int = self.index
        di: int = self.field.add(self.u[i], w[i])

        # Going to next unused ui and wi
        self.index += 1
        
        return i, di

    def open(self, wi: int, vi: int, index: int):
        return wi, vi, index