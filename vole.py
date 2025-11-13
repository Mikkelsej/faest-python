from field import ExtensionField
from prover import Prover
from verifier import Verifier


class Vole:
    """Vector Oblivious Linear Evaluation (VOLE) protocol

    VOLE establishes a correlation between a prover and verifier where:
    - Prover has vectors u and v
    - Verifier has vector q and secret Delta
    - The relationship q[i] = v[i] + u[i] * Delta holds for all i

    This correlation enables efficient zero-knowledge proofs through homomorphic
    operations on committed values.
    """

    def __init__(self, field: ExtensionField, length: int) -> None:
        """Initialize a VOLE instance

        Args:
            field (ExtensionField): finite field for computations
            length (int): length of the VOLE vectors
        """
        self.field: ExtensionField = field
        self.length: int = length
        self.u: list[int] = []
        self.v: list[int] = []

    def initialize_prover(self, prover: Prover) -> None:
        """Initialize the prover with random VOLE vectors

        Generates and assigns the prover's share of the VOLE correlation:
        - u: vector of random bits {0,1}^length
        - v: vector of random field elements from F_{2^λ}

        Args:
            prover (Prover): the prover instance to initialize
        """
        # Sets u as {0,1}^l
        self.u = [self.field.get_random_bit() for _ in range(self.length)]
        prover.set_u(self.u)

        # Sets v as {x}^l, where x ∈ F_{2^λ}
        self.v = [self.field.get_random() for _ in range(self.length)]
        prover.set_v(self.v)

    def initialize_verifier(self, verifier: Verifier) -> None:
        """Initialize the verifier with the VOLE correlation

        Generates and assigns the verifier's share of the VOLE correlation:
        - Delta: random secret field element from F_{2^λ}
        - q: vector where q[i] = v[i] + u[i] * Delta for all i

        The verifier learns Delta and q, but not u or v individually.

        Args:
            verifier (Verifier): the verifier instance to initialize
        """
        # Sets delta as x, where x ∈ F_{2^λ}
        delta = self.field.get_random()
        verifier.set_delta(delta)

        # Sets q as {q_i = v_i + u_i · delta} for i ∈ [length]
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
