from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vole import Vole

class Verifier:
    def __init__(self, vole: 'Vole') -> None:
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
