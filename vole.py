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

    def __init__(self, field: ExtensionField, vole_length: int) -> None:
        """Initialize a VOLE instance

        Args:
            field (ExtensionField): finite field for computations
            vole_length (int): number of fresh VOLE correlations to generate
            total_length (int): total size of the storage (vole_length + temporary variables)
        """
        self.a0 = 0
        self.a1 = 0
        self.field: ExtensionField = field
        self.vole_length: int = vole_length
        self.total_length: int = vole_length * 2
        self.u: list[int] = []
        self.v: list[int] = []

    def initialize_prover(self, prover: Prover) -> None:
        """Initialize the prover with random VOLE vectors

        Generates and assigns the prover's share of the VOLE correlation:
        - u: vector of random bits {0,1}^vole_length, followed by zeros
        - v: vector of random field elements from F_{2^λ}, followed by zeros

        Args:
            prover (Prover): the prover instance to initialize
        """
        # Sets u as {0,1}^l for the first vole_length elements
        self.u = [self.field.get_random_bit() for _ in range(self.vole_length)]
        # Pad with zeros for temporary storage
        self.u.extend([0] * (self.total_length - self.vole_length))
        prover.set_u(self.u)

        # Sets v as {x}^l, where x ∈ F_{2^λ} for the first vole_length elements
        self.v = [self.field.get_random() for _ in range(self.vole_length)]
        # Pad with zeros for temporary storage
        self.v.extend([0] * (self.total_length - self.vole_length))
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

        # Sets q as {q_i = v_i + u_i · delta} for i ∈ [total_length]
        # Note: for i >= vole_length, u[i] = 0 and v[i] = 0, so q[i] = 0
        q = [
            self.field.add(vi, self.field.mul(ui, delta))
            for (vi, ui) in zip(self.v, self.u)
        ]
        verifier.set_q(q)

    def get_random_vole_prover(self):
        self.u = [self.field.get_random_bit() for _ in range(self.vole_length)]
        self.v = [self.field.get_random() for _ in range(self.vole_length)]

        for i, ui in enumerate(self.u):
            self.a0 = self.field.add(self.a0, self.field.mul(ui, self.field.pow(2, i)))
        for i, vi in enumerate(self.v):
            self.a1 = self.field.add(self.a1, self.field.mul(vi, self.field.pow(2, i)))

        return self.a0, self.a1

    def get_random_vole_verifier(self):
        delta = self.field.get_random()
        b = self.field.add(self.a0, self.field.mul(self.a1, delta))

        return b, delta

if __name__ == "__main__":
    length: int = 1000
    field: ExtensionField = ExtensionField(8)
    vole = Vole(field, 1000)
    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)
