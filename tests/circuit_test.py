import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from circuit import Check0Gate, PowGate, Wire
from sudoku_circuit import SudokuCircuit
from prover import Prover
from verifier import Verifier
from vole import Vole
from field import ExtensionField
from sudoku_generator import SudokuGenerator


class TestSudokuCircuit:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.field = ExtensionField(8)
        # Increased VOLE capacity for num_rec gate which uses more commitments
        self.vole = Vole(self.field, 20000)
        self.prover = Prover(self.vole)
        self.verifier = Verifier(self.vole)
        self.sudoku_circuit = SudokuCircuit(self.prover, self.verifier, self.vole)
        generator = SudokuGenerator()
        self.part_sudoku = generator.part_sudoku
        self.solved_sudoku = generator.solution

    def test_column(self):
        circuit = self.sudoku_circuit
        col_wires = circuit.get_column_wires(0)
        assert len(col_wires) == 9
        for i in range(9):
            assert col_wires[i] == circuit.input_sudoku[i][0]

    def test_row(self):
        circuit = self.sudoku_circuit
        row_wires = circuit.get_row_wires(0)
        assert len(row_wires) == 9
        for i in range(9):
            assert row_wires[i] == circuit.input_sudoku[0][i]

    def test_box(self):
        circuit = self.sudoku_circuit
        box_wires = circuit.get_box_wires(0)
        assert len(box_wires) == 9
        for i in range(9):
            assert box_wires[i] == circuit.input_sudoku[i // 3][i % 3]

    def test_valid_sudoku_generation(self):

        valid_list = []
        for i, row in enumerate(self.part_sudoku):
            for j, value in enumerate(row):
                if value != 0:
                    solved_value = self.solved_sudoku[i][j]
                    valid = solved_value == value
                    valid_list.append(valid)
        assert all(valid_list)

    def test_pow_gate_valid(self):
        for i in range(1, 256):
            # Properly commit the value before creating the wire
            idx, di = self.prover.commit(i)
            self.verifier.update_q(idx, di)
            wire = Wire(idx)
            result_wire = PowGate([wire], self.prover, self.verifier).evaluate()
            assert result_wire.get_value(self.prover) == 1

        # Test with value 0
        idx, di = self.prover.commit(0)
        self.verifier.update_q(idx, di)
        wire = Wire(idx)
        result_wire = PowGate([wire], self.prover, self.verifier).evaluate()
        assert result_wire.get_value(self.prover) == 0

    def test_check_0_gate_valid(self):
        # Properly commit all zero values before creating wires
        wires: list[Wire] = []
        for _ in range(100):
            idx, di = self.prover.commit(0)
            self.verifier.update_q(idx, di)
            wires.append(Wire(idx))
        result_wire = Check0Gate(wires, self.prover, self.verifier).evaluate()
        assert result_wire.get_value(self.prover) == 0

    def test_check_0_gate_invalid(self):
        # Properly commit random values before creating wires
        wires: list[Wire] = []
        for _ in range(100):
            random_val = self.field.get_random()
            idx, di = self.prover.commit(random_val)
            self.verifier.update_q(idx, di)
            wires.append(Wire(idx))
        result_wire = Check0Gate(wires, self.prover, self.verifier).evaluate()
        assert not result_wire.get_value(self.prover) == 0

    def test_open_circuit(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for i in range(9):
            for j in range(9):
                bits = self.field.bit_dec(self.solved_sudoku[i][j], 4)
                bit_wires = circuit.bit_wires[i][j]
                for bit_idx, bit in enumerate(bits):
                    bit_wire = bit_wires[bit_idx]
                    vole_index = bit_wire.commitment_index
                    index, wi, vi = self.prover.open(vole_index)
                    assert self.verifier.check_open(wi, vi, index)

    def test_valid_row(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for row in circuit.input_sudoku:
            wire = circuit.validate_wires(row)
            assert wire.get_value(self.prover) == 0

    def test_valid_sudoku(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        result = circuit.is_valid()
        assert result

    def test_invalid_sudoku(self):
        """Test that an invalid sudoku returns False."""
        circuit = self.sudoku_circuit
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        # Make sudoku invalid by duplicating a value in the first row
        solved_sudoku[0][0] = solved_sudoku[0][1]

        circuit.commit_sudoku(solved_sudoku)

        result = circuit.is_valid()
        assert not result

    @pytest.mark.parametrize("iteration", range(100))
    def test_multiple_random_valid_sudokus(self, iteration):
        """Test that multiple randomly generated sudokus all validate correctly."""
        # Generate a new sudoku
        generator = SudokuGenerator()
        solved_sudoku = generator.solution

        # Create fresh instances for each test
        vole = Vole(self.field, 20000)
        prover = Prover(vole)
        verifier = Verifier(vole)
        circuit = SudokuCircuit(prover, verifier, vole)

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        assert result, f"Random sudoku #{iteration+1} failed validation"

    def test_known_valid_sudoku_1(self):
        """Test with a known valid sudoku puzzle #1."""
        circuit = self.sudoku_circuit
        known_sudoku = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    def test_known_valid_sudoku_2(self):
        """Test with a known valid sudoku puzzle #2."""
        circuit = self.sudoku_circuit
        known_sudoku = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    def test_known_valid_sudoku_3(self):
        """Test with a known valid sudoku puzzle #3."""
        circuit = self.sudoku_circuit
        known_sudoku = [
            [8, 2, 7, 1, 5, 4, 3, 9, 6],
            [9, 6, 5, 3, 2, 7, 1, 4, 8],
            [3, 4, 1, 6, 8, 9, 7, 5, 2],
            [5, 9, 3, 4, 6, 8, 2, 7, 1],
            [4, 7, 2, 5, 1, 3, 6, 8, 9],
            [6, 1, 8, 9, 7, 2, 4, 3, 5],
            [7, 8, 6, 2, 3, 5, 9, 1, 4],
            [1, 5, 4, 7, 9, 6, 8, 2, 3],
            [2, 3, 9, 8, 4, 1, 5, 6, 7]
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    def test_invalid_sudokus(self):
        """Test that invalid sudokus are correctly identified as invalid.
        We're checking for false negatives - invalid sudokus that incorrectly pass validation."""
        false_negatives = []
        for _ in range(100):
            vole1 = Vole(self.field, 4000)
            prover1 = Prover(vole1)
            verifier1 = Verifier(vole1)
            circuit1 = SudokuCircuit(prover1, verifier1, vole1)
            false_negatives.append(self.invalid_sudoku_duplicate_in_column(circuit1, prover1))

            vole2 = Vole(self.field, 4000)
            prover2 = Prover(vole2)
            verifier2 = Verifier(vole2)
            circuit2 = SudokuCircuit(prover2, verifier2, vole2)
            false_negatives.append(self.invalid_sudoku_duplicate_in_box(circuit2, prover2))

            vole3 = Vole(self.field, 4000)
            prover3 = Prover(vole3)
            verifier3 = Verifier(vole3)
            circuit3 = SudokuCircuit(prover3, verifier3, vole3)
            false_negatives.append(not self.all_rows_columns_boxes_individually(circuit3, prover3))

        prob_false_negatives = false_negatives.count(True) / len(false_negatives)
        assert prob_false_negatives < 0.05

    def invalid_sudoku_duplicate_in_column(self, circuit, prover):
        """Test that a sudoku with duplicates in a column is invalid."""
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        # Make sudoku invalid by duplicating a value in the first column
        solved_sudoku[0][0] = solved_sudoku[1][0]

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        return result

    def invalid_sudoku_duplicate_in_box(self, circuit, prover):
        """Test that a sudoku with duplicates in a 3x3 box is invalid."""
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        # Make sudoku invalid by duplicating a value in the first box
        # Copy value from (0,0) to (1,1) - both in top-left box
        solved_sudoku[1][1] = solved_sudoku[0][0]

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        return result

    def all_rows_columns_boxes_individually(self, circuit, prover):
        """Test that all rows, columns, and boxes validate individually for a correct sudoku."""
        circuit.commit_sudoku(self.solved_sudoku)

        # Test all rows
        for i in range(9):
            row_wires = circuit.get_row_wires(i)
            wire = circuit.validate_wires(row_wires)
            if wire.get_value(prover) != 0:
                return False

        # Test all columns
        for i in range(9):
            col_wires = circuit.get_column_wires(i)
            wire = circuit.validate_wires(col_wires)
            if wire.get_value(prover) != 0:
                return False

        # Test all boxes
        for i in range(9):
            box_wires = circuit.get_box_wires(i)
            wire = circuit.validate_wires(box_wires)
            if wire.get_value(prover) != 0:
                return False

        return True
