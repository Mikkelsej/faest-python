from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vole import Vole


class Verifier:
    """Verifier in a Vector Oblivious Linear Evaluation (VOLE) based commitment scheme

    The verifier maintains the q vector where q[i] = v[i] + Delta * w[i] for a secret
    Delta known only to the verifier. The verifier can verify operations on committed
    values without learning the actual values.
    """

    def __init__(self, vole: "Vole") -> None:
        """Initialize the verifier with a VOLE instance

        Args:
            vole (Vole): VOLE instance that provides the underlying commitment infrastructure
        """
        self.vole = vole
        self.field = vole.field
        self.delta: int = -1
        self.q: list[int] = []
        self.index: int = 0
        vole.initialize_verifier(self)

    def set_delta(self, delta: int) -> None:
        """Set the secret Delta value for the verification scheme

        Args:
            delta (int): secret field element known only to the verifier
        """
        self.delta = delta

    def set_q(self, q: list[int]) -> None:
        """Set the q vector for the commitment scheme

        Args:
            q (list[int]): vector of field elements where q[i] = v[i] + Delta * w[i]
        """
        self.q = q

    def update_q(self, index: int, di: int) -> None:
        """Update q[i] with a correction value from the prover

        When the prover commits to a new value, it sends a correction di that allows
        the verifier to update q[i] = q[i] + di * Delta without learning the committed value.

        Args:
            index (int): the index to update
            di (int): correction value from the prover
        """
        i: int = index
        qi: int = self.field.add(self.q[i], self.field.mul(di, self.delta))
        self.q[i] = qi
        if i == self.index:
            self.index += 1

    def check_open(self, wi: int, vi: int, index: int) -> bool:
        """Verify that an opened commitment is valid

        Checks that q[index] = v[index] + w[index] * Delta by recomputing the
        expected q value from the revealed w and v values.

        Args:
            wi (int): the revealed w value
            vi (int): the revealed v value
            index (int): the commitment index

        Returns:
            bool: True if the opening is valid, False otherwise
        """
        original_qi: int = self.q[index]

        new_qi = self.field.add(vi, self.field.mul(wi, self.delta))

        if original_qi == new_qi:
            return True

        return False

    def add(self, index_a: int, index_b: int) -> int:
        """Add two committed values and return the result index

        Performs homomorphic addition: q[c] = q[a] + q[b]
        This works because addition is linear in the commitment scheme.

        Args:
            index_a (int): index of the first value
            index_b (int): index of the second value

        Returns:
            int: index c where the sum is stored
        """
        c = self.index
        self.index += 1

        # q[c] = q[a] + q[b] (addition is linear, no correction needed)
        self.q[c] = self.field.add(self.q[index_a], self.q[index_b])

        return c

    def sub(self, index_a: int, index_b: int) -> int:
        """Subtract two committed values (a - b) and return the result index

        Performs homomorphic subtraction: q[c] = q[a] - q[b]
        This works because subtraction is linear in the commitment scheme.

        Args:
            index_a (int): index of the first value (minuend)
            index_b (int): index of the second value (subtrahend)

        Returns:
            int: index c where the difference is stored
        """
        c = self.index
        self.index += 1

        # q[c] = q[a] - q[b] (subtraction is linear, no correction needed)
        self.q[c] = self.field.sub(self.q[index_a], self.q[index_b])

        return c

    def mul(self, index_a: int, index_b: int, correction: int) -> int:
        """Allocate result index and apply correction for multiplication

        Multiplication is not linear, so the prover must send a correction value.
        This method updates q[c] using the correction without learning the actual values.

        Args:
            index_a (int): index of the first value
            index_b (int): index of the second value
            correction (int): correction value from the prover

        Returns:
            int: index c where the product is stored
        """
        c = self.index
        self.index += 1

        # Apply the correction to q[c]
        self.update_q(c, correction)

        return c

    def check_mul(self, index_a: int, index_b: int, index_c: int, d: int, e: int) -> bool:
        """Verify that a multiplication was performed correctly

        Checks that q[a] * q[b] - Delta * q[c] = Delta * d + e
        This verifies that w[c] = w[a] * w[b] without the verifier learning the values.

        Args:
            index_a (int): index of the first value
            index_b (int): index of the second value
            index_c (int): index of the product
            d (int): linear verification component from prover
            e (int): quadratic verification component from prover

        Returns:
            bool: True if the multiplication is valid, False otherwise
        """
        delta: int = self.delta

        lhs: int = self.field.sub(
            self.field.mul(self.q[index_a], self.q[index_b]), self.field.mul(delta, self.q[index_c])
        )

        rhs: int = self.field.add(self.field.mul(d, delta), e)

        return lhs == rhs
