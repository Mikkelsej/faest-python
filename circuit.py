"""Circuit builder and constraints for Sudoku over VOLE-backed arithmetic."""

from abc import ABC, abstractmethod
from prover import Prover
from verifier import Verifier


class Wire:
    """A wire is a reference to a committed value in the VOLE scheme."""

    def __init__(self, commitment_index: int):
        self.commitment_index: int = commitment_index

    def get_value(self, prover: Prover) -> int:
        """Get the actual value from the prover's committed values."""
        return prover.u[self.commitment_index]


class Gate(ABC):
    """Abstract base class for gates in the arithmetic circuit."""

    def __init__(self, inputs: list[Wire], prover: Prover, verifier: Verifier):
        self.inputs: list[Wire] = inputs
        self.prover: Prover = prover
        self.verifier: Verifier = verifier

    @abstractmethod
    def evaluate(self) -> Wire:
        """Evaluate the gate and return the output wire."""
        pass


class AddGate(Gate):
    """Addition gate: output = sum of all inputs."""

    def evaluate(self) -> Wire:
        commitment_index = self.inputs[0].commitment_index
        for i in range(len(self.inputs) - 1):
            next_input_index = self.inputs[i + 1].commitment_index
            prover_idx = self.prover.add(commitment_index, next_input_index)
            self.verifier.add(commitment_index, next_input_index)
            commitment_index = prover_idx

        return Wire(commitment_index)


class MulGate(Gate):
    """Multiplication gate: output = product of all inputs."""

    def evaluate(self) -> Wire:
        commitment_index = self.inputs[0].commitment_index
        for i in range(len(self.inputs) - 1):
            next_input_index = self.inputs[i + 1].commitment_index
            result_idx, correction, d, e = self.prover.mul(
                commitment_index, next_input_index
            )
            self.verifier.mul(commitment_index, next_input_index, correction)
            commitment_index = result_idx

        return Wire(commitment_index)


class PowGate(Gate):
    """Power gate: raises a single input to a given power.

    Computes input^power
    """

    def __init__(self, input_wire: Wire, prover: Prover, verifier: Verifier, power: int):
        super().__init__([input_wire], prover, verifier)
        self.power = power

    def evaluate(self) -> Wire:
        if self.power == 0:
            # x^0 = 1
            idx, di = self.prover.commit(1)
            self.verifier.update_q(idx, di)
            return Wire(idx)

        if self.power == 1:
            # x^1 = x
            return self.inputs[0]

        # For power >= 2, use repeated multiplication
        # Start with the base value
        result_idx = self.inputs[0].commitment_index
        base_idx = self.inputs[0].commitment_index

        # Multiply (power - 1) times to get base^power
        for _ in range(self.power - 1):
            old_result_idx = result_idx
            result_idx, correction, d, e = self.prover.mul(old_result_idx, base_idx)
            self.verifier.mul(old_result_idx, base_idx, correction)

        return Wire(result_idx)


class NumRecGate(Gate):
    """Number reconstruction gate: reconstructs a field element from polynomial coefficients.

    In an extension field F_{2^m}, elements are polynomials: \sum b_i * x^i
    This gate computes this polynomial representation using only linear operations.
    """

    def evaluate(self) -> Wire:
        result_idx = None

        for i, coeff_wire in enumerate(self.inputs):
            if i == 0:
                result_idx = coeff_wire.commitment_index
            else:
                x_power = self.prover.field.pow(2, i)

                product_idx = self.prover.scalar_mul(coeff_wire.commitment_index, x_power)
                self.verifier.scalar_mul(coeff_wire.commitment_index, x_power)

                new_result_idx = self.prover.add(result_idx, product_idx)
                self.verifier.add(result_idx, product_idx)
                result_idx = new_result_idx

        return Wire(result_idx)


class Check0Gate(Gate):
    """Check-zero gate: returns 0 iff all inputs are 0."""

    def evaluate(self) -> Wire:
        wires: list[Wire] = []
        idx_1, di = self.prover.commit(1)
        self.verifier.update_q(idx_1, di)
        wire_1 = Wire(idx_1)

        for wire in self.inputs:
            gate = PowGate(wire, self.prover, self.verifier, 2**self.prover.field.m - 1)
            wire = gate.evaluate()
            wires.append(wire)

        wires_2: list[Wire] = []
        for wire in wires:
            gate = AddGate([wire, wire_1], self.prover, self.verifier)
            wire = gate.evaluate()
            wires_2.append(wire)

        gate = MulGate(wires_2, self.prover, self.verifier)
        wire = gate.evaluate()

        gate = AddGate([wire, wire_1], self.prover, self.verifier)
        return gate.evaluate()
