from prover import Prover
from verifier import Verifier
from extensionfield import ExtensionField
import random


class Vole:
    def __init__(self, m: int, length: int) -> None:
        self.field: ExtensionField = ExtensionField(m)
        self.length: int = length
        self.prover: Prover = Prover(self.field, 1000)
        self.verifier: Verifier = Verifier(self.field)

    def initialValues(self, prover: Prover, verifier: Verifier):
        u = [random.randint(0, 1) for _ in range(self.length)]
        prover.setU(u)

        v = [self.field.getRandom() for _ in range(self.length)]
        prover.setV(v)

        delta = self.field.getRandom()
        verifier.setDelta(delta)

        q = [vi + ui * delta for (vi, ui) in zip(v, u)]
        verifier.setQ(q)

    def commit(self, w):
        ui = self.prover.u[0]
        vi = self.prover.v[0]

        di = ui ^ vi

        qi = (self.qs[0] + di * self.verifier.delta) % 2

    def open(self, u, v):
        pass


vole = Vole(8, 1000)

print(vole.prover.v)
print(vole.prover.u)
print(vole.verifier.delta)
