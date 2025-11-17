"""Abstract validator interface and concrete implementations for Sudoku circuit validation."""

from abc import ABC, abstractmethod
from circuit import Wire, AddGate, SquareGate, CubeGate, Check0Gate


class SudokuValidator(ABC):
    """Abstract base class for Sudoku validation strategies."""

    @abstractmethod
    def validate_wires(self, wires: list[Wire], circuit) -> Wire:
        """Validate that wires represent a permutation (1..9).

        Args:
            wires: List of 9 wires representing values in a row/column/box
            circuit: The SudokuCircuit instance (for accessing prover/verifier)

        Returns:
            Wire that evaluates to 0 if and only if the permutation is valid
        """
        pass

    @abstractmethod
    def is_valid(self, circuit) -> bool:
        """Validate the entire sudoku puzzle.

        Args:
            circuit: The SudokuCircuit instance to validate

        Returns:
            True if the sudoku is valid, False otherwise
        """
        pass


class PITValidator(SudokuValidator):
    """Polynomial Identity Testing (PIT) based validator.

    Uses the product (r - x_i) = (r - 1)(r - 2)...(r - 9) identity
    to verify that each row/column/box contains a permutation of 1..9.
    """

    def validate_wires(self, wires: list[Wire], circuit) -> Wire:
        """Validate that wires represent a permutation (1..9) using PIT.

        Computes \prod(r - x_i) for the given wires and compares to the expected
        polynomial \prod(r - i) for i=1..9.

        Args:
            wires: List of 9 wires representing values in a row/column/box
            circuit: The SudokuCircuit instance

        Returns:
            Wire that evaluates to 0 if and only if the permutation is valid
        """
        prover = circuit.prover
        verifier = circuit.verifier
        challenge_wire = circuit.challenge_wire

        # Compute \prod(r - x_i) for the wires
        result_idx = prover.sub(challenge_wire.commitment_index, wires[0].commitment_index)
        verifier.sub(challenge_wire.commitment_index, wires[0].commitment_index)

        for i in range(1, 9):
            diff_idx = prover.sub(challenge_wire.commitment_index, wires[i].commitment_index)
            verifier.sub(challenge_wire.commitment_index, wires[i].commitment_index)

            result_idx, correction, d, e = prover.mul(result_idx, diff_idx)
            verifier.mul(result_idx, diff_idx, correction)

        # Compare to expected polynomial: \prod(r - i) for i=1..9
        result_wire = Wire(result_idx)
        diff_gate = AddGate([result_wire, circuit.expected_poly_wire], prover, verifier)
        return diff_gate.evaluate()

    def is_valid(self, circuit) -> bool:
        """Validate the entire sudoku puzzle by opening 27 validation values.

        Checks all 9 rows, 9 columns, and 9 boxes using PIT validation.

        Args:
            circuit: The SudokuCircuit instance to validate

        Returns:
            True if all 27 validations pass, False if any validation fails
        """
        prover = circuit.prover
        verifier = circuit.verifier
        valid_wires = []

        # Validate all rows, columns, and boxes
        for i in range(9):
            row = circuit.get_row_wires(i)
            valid = self.validate_wires(row, circuit)
            valid_wires.append(valid)

            col = circuit.get_column_wires(i)
            valid = self.validate_wires(col, circuit)
            valid_wires.append(valid)

            box = circuit.get_box_wires(i)
            valid = self.validate_wires(box, circuit)
            valid_wires.append(valid)

        # Open all validation wires and check they are all 0
        for idx, valid_wire in enumerate(valid_wires):
            vole_index = valid_wire.commitment_index
            opened_index, wi, opened_vi = prover.open(vole_index)

            if not verifier.check_open(wi, opened_vi, opened_index):
                return False

            if wi != 0:
                return False

        return True

class Check0Validator(SudokuValidator):
    """Check-zero validator."""

    def validate_wires(self, wires: list[Wire], circuit) -> Wire:
        """Validate that wires represent a permutation (1..9)."""

        squared_wires: list[Wire] = []
        cubed_wires: list[Wire] = []

        for wire in wires:
            square_gate = SquareGate([wire], circuit.prover, circuit.verifier)
            squared_wires.append(square_gate.evaluate())

            cube_gate = CubeGate([wire], circuit.prover, circuit.verifier)
            cubed_wires.append(cube_gate.evaluate())

        add_gate_square = AddGate(squared_wires, circuit.prover, circuit.verifier)
        # For 1..9 permutation sum of squares equals 1 (in the field)
        # Create a public constant wire by committing to 0 and adding the constant
        zero_index, correction_zero = circuit.prover.commit(0)
        circuit.verifier.update_q(zero_index, correction_zero)
        expected_square_value = 1
        expected_square_index = circuit.prover.add_constant(zero_index, expected_square_value)
        circuit.verifier.add_constant(zero_index, expected_square_value)
        result_square_gate = AddGate([add_gate_square.evaluate(), Wire(expected_square_index)], circuit.prover, circuit.verifier)
        result_square_wire = result_square_gate.evaluate()

        add_gate_cube = AddGate(cubed_wires, circuit.prover, circuit.verifier)
        # For 1..9 permutation sum of cubes equals 73 (in the field)
        expected_cube_value = 73
        expected_cube_index = circuit.prover.add_constant(zero_index, expected_cube_value)
        circuit.verifier.add_constant(zero_index, expected_cube_value)
        result_cube_gate = AddGate([add_gate_cube.evaluate(), Wire(expected_cube_index)], circuit.prover, circuit.verifier)
        result_cube_wire = result_cube_gate.evaluate()

        result_wire = Check0Gate([result_square_wire, result_cube_wire], circuit.prover, circuit.verifier).evaluate()
        return result_wire

    def is_valid(self, circuit) -> bool:
        """Validate the entire sudoku puzzle by checking that all 81 wires are 0."""
        prover = circuit.prover
        verifier = circuit.verifier
        valid_wires = []

        # Validate all rows, columns, and boxes
        for i in range(9):
            row = circuit.get_row_wires(i)
            valid = self.validate_wires(row, circuit)
            valid_wires.append(valid)

            col = circuit.get_column_wires(i)
            valid = self.validate_wires(col, circuit)
            valid_wires.append(valid)

            box = circuit.get_box_wires(i)
            valid = self.validate_wires(box, circuit)
            valid_wires.append(valid)

        result_wire = Check0Gate(valid_wires, prover, verifier).evaluate()
        index, wi, vi = prover.open(result_wire.commitment_index)
        open_valid = verifier.check_open(wi, vi, index)
        if not open_valid:
            return False

        return result_wire.get_value(prover) == 0

