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
        self.initialValues(self.prover, self.verifier)

    def initialValues(self, prover: Prover, verifier: Verifier):
        # Sets u as {0,1}^l
        u = [random.randint(0, 1) for _ in range(self.length)]
        prover.setU(u)

        # Sets v as {x}^l, where x\in F_{2^\lambda}
        v = [self.field.getRandom() for _ in range(self.length)]
        prover.setV(v)

        # Sets delta as x, where x\in F_{2^\lambda}
        delta = self.field.getRandom()
        verifier.setDelta(delta)


        # Sets q as {q_i = v_i + u_i \cdot delta} for i \in l
        q = [vi + ui * delta for (vi, ui) in zip(v, u)]
        verifier.setQ(q)

    def commit(self, w: list[int], index: int):
        ui: int = self.prover.u[index]
        #vi: int = self.prover.v[index]
        wi: int = w[index]

        di: int = ui ^ wi

        qi: int = (self.verifier.q[index] + di * self.verifier.delta)

        self.verifier.q[index] = qi
        
    def open(self, wi: int, vi: int, index: int):
        qi = vi+wi*self.verifier.delta
        self.verifier.check(qi, index)


vole = Vole(8, 1000)

print(vole.prover.v)
print(vole.prover.u)
print(vole.verifier.delta)
