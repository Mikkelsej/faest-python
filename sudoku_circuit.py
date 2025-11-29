from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier
from sudoku_generator import SudokuGenerator
from sudoku_validator import SudokuValidator, PITValidator
from circuit import (
    AddGate,
    NumRecGate,
    Wire,
)


class SudokuCircuit:
    def __init__(
        self,
        prover: Prover,
        verifier: Verifier,
        vole: Vole,
        validator: SudokuValidator
    ):
        self.prover = prover
        self.verifier = verifier
        self.vole = vole
        self.validator = validator
        self.input_sudoku: list[list[Wire]] = [
            [Wire(0) for _ in range(9)] for _ in range(9)
        ]

        self.challenge: int = 0
        self.challenge_wire: Wire = Wire(0)
        self._generate_challenge()

        self.expected_poly_wire: Wire = self._compute_expected_polynomial()

    def _generate_challenge(self) -> Wire:
        # Generate a random challenge and commit it once for reuse
        self.challenge = self.verifier.field.get_random()

        # Create a public wire with the computed polynomial value
        zero_idx, di = self.prover.commit(0)
        self.verifier.update_q(zero_idx, di)

        r_idx = self.prover.add_constant(zero_idx, self.challenge)
        self.verifier.add_constant(zero_idx, self.challenge)

        self.challenge_wire: Wire = Wire(r_idx)
        return self.challenge_wire

    def _compute_expected_polynomial(self) -> Wire:
        """Compute the prod (r - i) for i=1..9.
        Used for polynomial identity testing.
        """
        # Compute the polynomial (r-1)(r-2)...(r-9) using field arithmetic
        # This is a public value
        result = 1
        for i in range(1, 10):
            # Compute (r - i)
            diff = self.vole.field.sub(self.challenge, i)
            # Multiply into result
            result = self.vole.field.mul(result, diff)

        # Create a public wire with the computed polynomial value
        zero_idx, di = self.prover.commit(0)
        self.verifier.update_q(zero_idx, di)

        result_idx = self.prover.add_constant(zero_idx, result)
        self.verifier.add_constant(zero_idx, result)

        return Wire(result_idx)

    def create_wire(self, bit_wires: list[Wire], i: int, j: int):
        """Reconstruct a value from bit wires using num_rec gate.

        Args:
            bit_wires: List of wires representing bits (LSB to MSB)
            i: Row index
            j: Column index
        """
        # Use num_rec gate to reconstruct the value from bits
        num_rec_gate = NumRecGate(bit_wires, self.prover, self.verifier)
        reconstructed_wire = num_rec_gate.evaluate()
        self.input_sudoku[i][j] = reconstructed_wire

    def get_column_wires(self, col_index: int) -> list[Wire]:
        """Extract all wires from a specific column.

        Args:
            col_index: Column index (0-8)

        Returns:
            List of wires in the specified column
        """
        return [self.input_sudoku[i][col_index] for i in range(9)]

    def get_row_wires(self, row_index: int) -> list[Wire]:
        """Extract all wires from a specific row.

        Args:
            row_index: Row index (0-8)

        Returns:
            List of wires in the specified row
        """
        return [self.input_sudoku[row_index][i] for i in range(9)]

    def get_box_wires(self, box_index: int) -> list[Wire]:
        """Extract all wires from a specific 3x3 box.

        Box indices (0-8):
        0 1 2
        3 4 5
        6 7 8

        Args:
            box_index: Box index (0-8)

        Returns:
            List of 9 wires in the specified box
        """
        box_row = (box_index // 3) * 3
        box_col = (box_index % 3) * 3

        box_wires = []
        for i in range(3):
            for j in range(3):
                row_idx = box_row + i
                col_idx = box_col + j
                box_wires.append(self.input_sudoku[row_idx][col_idx])

        return box_wires

    def commit_sudoku(self, sudoku: list[list[int]]):
        for i, row in enumerate(sudoku):
            for j, value in enumerate(row):
                bits = self.vole.field.bit_dec(value, 4)

                # Commit each bit and create a wire for it
                bit_wires = []
                for bit in bits:
                    vole_index, di = self.prover.commit(bit)
                    self.verifier.update_q(vole_index, di)
                    # Create a wire for this bit
                    bit_wire = Wire(vole_index)
                    bit_wires.append(bit_wire)

                # Use num_rec gate to reconstruct the full value
                self.create_wire(bit_wires, i, j)

    def validate_wires(self, wires: list[Wire]) -> Wire:
        """Validate that wires represent a permutation (1..9).

        Delegates to the configured validator strategy.

        Args:
            wires: List of 9 wires representing values in a row/column/box

        Returns:
            Wire that evaluates to 0 if and only if the permutation is valid
        """
        return self.validator.validate_wires(wires, self)

    def is_valid(self) -> bool:
        """Validate the entire sudoku puzzle.

        Delegates to the configured validator strategy.

        Returns:
            True if the sudoku is valid, False otherwise.
        """
        return self.validator.is_valid(self)

if __name__ == "__main__":
    field = ExtensionField(64)
    vole_length = 1400
    vole = Vole(field, vole_length)
    sudoku = SudokuGenerator()
    prover = Prover(vole)
    verifier = Verifier(vole)

    part_sudoku = sudoku.part_sudoku

    circuit = SudokuCircuit(prover, verifier, vole, PITValidator())

    solved_sudoku = sudoku.solution

    circuit.commit_sudoku(solved_sudoku)

    print("Sudoku committed:")
    for row in circuit.input_sudoku:
        for wire in row:
            print(prover.u[wire.commitment_index], end=" ")
        print()

    print("Is valid:", circuit.is_valid())
    print("used: ", prover.index) # 1377 indexes
