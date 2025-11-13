from typing import TYPE_CHECKING
from field import ExtensionField

if TYPE_CHECKING:
    from vole import Vole


class Prover:
    """Prover in a Vector Oblivious Linear Evaluation (VOLE) based commitment scheme

    The prover maintains secret values u and v where the commitment relationship is:
    w[i] = u[i] + Delta * v[i] for some global Delta known only to the verifier.
    The prover can commit to values and perform operations on committed values.
    """

    def __init__(self, vole: "Vole") -> None:
        """Initialize the prover with a VOLE instance

        Args:
            vole (Vole): VOLE instance that provides the underlying commitment infrastructure
        """
        self.vole = vole
        self.field: ExtensionField = vole.field
        self.length: int = vole.length

        self.u: list[int] = []
        self.v: list[int] = []

        self.index: int = 0

        vole.initialize_prover(self)

    def set_u(self, u: list[int]) -> None:
        """Set the u vector for the commitment scheme

        Args:
            u (list[int]): vector of field elements representing the first component
        """
        self.u = u

    def set_v(self, v: list[int]) -> None:
        """Set the v vector for the commitment scheme

        Args:
            v (list[int]): vector of field elements representing the second component
        """
        self.v = v

    def commit(self, w: int) -> tuple[int, int]:
        """Commit to a value w at the current index

        The commitment updates u[i] to w and computes the correction di = old_u[i] + w.
        This allows the verifier to maintain consistency without learning w.

        Args:
            w (int): value to commit to

        Returns:
            tuple[int, int]: (index, correction) where index is the commitment position
                           and correction is di = old_u[i] + w
        """
        i: int = self.index
        di: int = self.field.add(self.u[i], w)

        self.u[i] = w

        # Going to the next unused ui and wi
        self.index += 1

        return i, di

    def open(self, index: int) -> tuple[int, int, int]:
        """Open a commitment by revealing the underlying values

        Args:
            index (int): the commitment index to open

        Returns:
            tuple[int, int, int]: (index, u_i, v_i) - the opened commitment values
                                 where u_i and v_i are the prover's secret values
        """
        return index, self.u[index], self.v[index]

    def add(self, a: int, b: int) -> int:
        """Add two committed values and return the result index

        Performs homomorphic addition: w[c] = w[a] + w[b]
        This is achieved by setting u[c] = u[a] + u[b] and v[c] = v[a] + v[b]

        Args:
            a (int): index of the first value
            b (int): index of the second value

        Returns:
            int: index c where the sum is stored
        """
        c = self.index
        self.index += 1

        self.v[c] = self.field.add(self.v[a], self.v[b])
        self.u[c] = self.field.add(self.u[a], self.u[b])

        return c

    def sub(self, a: int, b: int) -> int:
        """Subtract two committed values (a - b) and return the result index

        Performs homomorphic subtraction: w[c] = w[a] - w[b]
        This is achieved by setting u[c] = u[a] - u[b] and v[c] = v[a] - v[b]

        Args:
            a (int): index of the first value (minuend)
            b (int): index of the second value (subtrahend)

        Returns:
            int: index c where the difference is stored
        """
        c = self.index
        self.index += 1

        self.v[c] = self.field.sub(self.v[a], self.v[b])
        self.u[c] = self.field.sub(self.u[a], self.u[b])

        return c

    def scalar_mul(self, a: int, scalar: int) -> int:
        """Multiply a committed value by a public constant (scalar)

        This is a linear operation requiring no communication with the verifier.
        Computes w[c] = scalar * w[a] by setting:
        - u[c] = scalar * u[a]
        - v[c] = scalar * v[a]

        Args:
            a (int): index of the value to multiply
            scalar (int): public constant to multiply by

        Returns:
            int: index c where the result is stored
        """
        c = self.index
        self.index += 1

        self.u[c] = self.field.mul(scalar, self.u[a])
        self.v[c] = self.field.mul(scalar, self.v[a])

        return c

    def mul(self, a: int, b: int) -> tuple[int, int, int, int]:
        """Multiply two committed values and return verification information

        Multiplication requires interaction since w[c] = w[a] * w[b] cannot be computed
        homomorphically from the linear relationship. The prover computes:
        - u[c] = u[a] * u[b]
        - correction = uc - old_u[c]
        - d = v[a]*u[b] + v[b]*u[a] - v[c] (linear component)
        - e = v[a]*v[b] (quadratic component)

        The verifier uses d and e to check that w[c] = w[a] * w[b] + Delta*d + Delta^2*e

        Args:
            a (int): index of the first value
            b (int): index of the second value

        Returns:
            tuple[int, int, int, int]: (result_index, correction, d, e) where:
                - result_index: index c where product is stored
                - correction: adjustment to u[c]
                - d: linear verification component
                - e: quadratic verification component
        """
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
