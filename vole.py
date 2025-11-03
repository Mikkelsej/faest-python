from field import ExtensionField
from prover import Prover
from verifier import Verifier


class Vole:
    def __init__(self, field: ExtensionField, length: int) -> None:
        self.field: ExtensionField = field
        self.length: int = length
        self.u: list[int]
        self.v: list[int]

    def initialize_prover(self, prover: Prover) -> None:
        # Sets u as {0,1}^l
        self.u = [self.field.get_random_bit() for _ in range(self.length)]
        prover.set_u(self.u)

        # Sets v as {x}^l, where x\in F_{2^\lambda}
        self.v = [self.field.get_random() for _ in range(self.length)]
        prover.set_v(self.v)

    def initialize_verifier(self, verifier: Verifier) -> None:
        # Sets delta as x, where x\in F_{2^\lambda}
        delta = self.field.get_random()
        verifier.set_delta(delta)

        # Sets q as {q_i = v_i + u_i \cdot delta} for i \in l
        q = [
            self.field.add(vi, self.field.mul(ui, delta))
            for (vi, ui) in zip(self.v, self.u)
        ]
        verifier.set_q(q)

if __name__ == "__main__":
    length: int = 1000
    field: ExtensionField = ExtensionField(8)
    vole = Vole(field, 1000)
    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)
