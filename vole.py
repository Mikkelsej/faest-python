from field import ExtensionField
from prover import Prover
from verifier import Verifier


class Vole:
    def __init__(self, field: ExtensionField, length: int) -> None:
        self.field: ExtensionField = field
        self.length: int = length
        self.u: list[int]
        self.v: list[int]
        self.delta: int
        self.q: list[int]

    def initialize_prover(self, prover: Prover) -> None:
        # Sets u as {0,1}^l
        self.u = [self.field.get_random_bit() for _ in range(self.length)]
        prover.set_u(self.u)

        # Sets v as {x}^l, where x\in F_{2^\lambda}
        self.v = [self.field.get_random() for _ in range(self.length)]
        prover.set_v(self.v)

    def initialize_verifier(self, verifier: Verifier) -> None:
        # Sets delta as x, where x\in F_{2^\lambda}
        self.delta = self.field.get_random()
        verifier.set_delta(self.delta)

        # Sets q as {q_i = v_i + u_i \cdot delta} for i \in l
        self.q = [
            self.field.add(vi, self.field.mul(ui, self.delta))
            for (vi, ui) in zip(self.v, self.u)
        ]
        verifier.set_q(self.q)

    def commit(self, index: int, di: int) -> None:
        qi: int = self.field.add(self.q[index], di * self.delta)
        self.q[index] = qi


if __name__ == "__main__":
    length: int = 1000
    field: ExtensionField = ExtensionField(8)
    vole = Vole(field, 1000)
    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)
