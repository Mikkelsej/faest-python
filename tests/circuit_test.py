import sys
import os
import pytest

from circuit import Gate, Wire

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
        self.vole = Vole(self.field, 2500000)
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
            assert Gate("pow", [Wire(i, i)], self.prover, self.verifier).evaluate() == 1
        assert Gate("pow", [Wire(0, 0)], self.prover, self.verifier).evaluate() == 0

    def test_check_0_gate_valid(self):
        wires: list[Wire] = [Wire(0, i) for i in range(1000)]
        assert Gate("check_0", wires, self.prover, self.verifier).evaluate() == 0

    def test_check_0_gate_invalid(self):
        wires: list[Wire] = [Wire(self.field.get_random(), i) for i in range(1000)]
        assert not Gate("check_0", wires, self.prover, self.verifier).evaluate() == 0

    def test_open_circuit(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for i, row in enumerate(circuit.input_sudoku):
            for j, wire in enumerate(row):
                vole_index = wire.commitment_index
                bits = self.field.bit_dec(self.solved_sudoku[i][j], self.field.m)
                for bit_idx, bit in enumerate(bits):
                    wi, vi, index = self.prover.open(
                        bit, self.prover.v[vole_index + bit_idx], vole_index + bit_idx
                    )
                    assert self.verifier.check_open(wi, vi, index)

    def test_valid_row(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for i, row in enumerate(circuit.input_sudoku):
            wire = circuit.validate_wires(row)
            assert wire.value == 0

    def test_valid_sudoku(self):
        """Test that a valid sudoku returns a wire with value 0."""
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value == 0, "Valid sudoku should return a wire with value 0"

    def test_invalid_sudoku(self):
        """Test that an invalid sudoku returns a wire with non-zero value."""
        circuit = self.sudoku_circuit
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        # Make sudoku invalid by duplicating a value in the first row
        solved_sudoku[0][0] = solved_sudoku[0][1]

        circuit.commit_sudoku(solved_sudoku)

        result_wire = circuit.is_valid2()
        assert (
            result_wire.value != 0
        ), "Invalid sudoku should return a wire with non-zero value"

    @pytest.mark.parametrize("iteration", range(1000))
    def test_all_sudoku_violation_types(self, iteration: int) -> None:
        """Test that the circuit detects all types of sudoku violations."""

        # Create a fresh VOLE for this iteration to avoid exhausting capacity
        vole = Vole(self.field, 15000)

        # Test 1: Row violation - duplicate in row 0
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        invalid_sudoku = [row[:] for row in self.solved_sudoku]
        invalid_sudoku[0][0] = invalid_sudoku[0][1]  # Duplicate in row
        circuit.commit_sudoku(invalid_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value != 0, "Row violation should be detected"

        # Test 2: Column violation - duplicate in column 0
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        invalid_sudoku = [row[:] for row in self.solved_sudoku]
        invalid_sudoku[0][0] = invalid_sudoku[1][0]  # Duplicate in column
        circuit.commit_sudoku(invalid_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value != 0, "Column violation should be detected"

        # Test 3: Box violation - duplicate in top-left 3x3 box
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        invalid_sudoku = [row[:] for row in self.solved_sudoku]
        # Make sure we're creating a box violation without row/column violation
        # Swap two values in the same box but different row and column
        temp = invalid_sudoku[0][0]
        invalid_sudoku[0][0] = invalid_sudoku[1][1]
        invalid_sudoku[1][1] = temp
        # Now create a duplicate in the box
        invalid_sudoku[0][2] = invalid_sudoku[0][
            0
        ]  # This creates both box and row violation
        circuit.commit_sudoku(invalid_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value != 0, "Box violation should be detected"

        # Test 4: Multiple violations
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        invalid_sudoku = [row[:] for row in self.solved_sudoku]
        invalid_sudoku[0][0] = invalid_sudoku[0][1]  # Row violation
        invalid_sudoku[2][2] = invalid_sudoku[3][2]  # Column violation
        invalid_sudoku[5][5] = invalid_sudoku[5][6]  # Another row violation
        circuit.commit_sudoku(invalid_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value != 0, "Multiple violations should be detected"

        # Test 5: Valid sudoku should return 0
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        circuit.commit_sudoku(self.solved_sudoku)
        result_wire = circuit.is_valid2()
        assert result_wire.value == 0, "Valid sudoku should return 0"

        # Test 6: All same value (extreme invalid case)
        circuit = SudokuCircuit(Prover(vole), Verifier(vole), vole)
        invalid_sudoku = [[1 for _ in range(9)] for _ in range(9)]
        circuit.commit_sudoku(invalid_sudoku)
        result_wire = circuit.is_valid2()
        assert (
            result_wire.value != 0
        ), "Sudoku with all same values should be detected as invalid"
