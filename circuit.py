from vole import Vole
from prover import Prover
from verifier import Verifier


class Circuit:
    def __init__(self, vole: Vole, prover: Prover, verifier: Verifier) -> None:
        self.vole: Vole = vole
        self.prover: Prover = prover
        self.verifier: Verifier = verifier

    def addition_gate(self, index_a: int, index_b: int):
        self.prover.add(index_a, index_b)
        self.verifier.add(index_a, index_b)

    def multiplication_gate(self, index_a: int, index_b: int):
        index_c, correction = self.prover.mul_commit(index_a, index_b)
        self.verifier.update_q(index_c, correction)

        d, e = self.prover.mul(index_a, index_b, index_c)
        is_valid: bool = self.verifier.check_mul(index_a, index_b, index_c, d, e)
        return is_valid
