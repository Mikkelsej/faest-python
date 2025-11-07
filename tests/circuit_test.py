import sys
import os
import pytest

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
        self.vole = Vole(self.field, 2000)
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
            assert box_wires[i] == circuit.input_sudoku[i//3][i%3]

    def test_valid_sudoku_generation(self):

        valid_list = []
        for i, row in enumerate(self.part_sudoku):
            for j, value in enumerate(row):
                if value != 0:
                    solved_value = self.solved_sudoku[i][j]
                    valid = solved_value == value
                    valid_list.append(valid)
        assert all(valid_list)


    def test_open_circuit(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for i, row in enumerate(circuit.input_sudoku):
            for j, wire in enumerate(row):
                vole_index = wire.commitment_index
                bits = self.field.bit_dec(self.solved_sudoku[i][j], self.field.m)
                for bit_idx, bit in enumerate(bits):
                    wi, vi, index = self.prover.open(bit, self.prover.v[vole_index+bit_idx], vole_index+bit_idx)
                    assert self.verifier.check_open(wi, vi, index)

    def test_valid_row(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        for i, row in enumerate(circuit.input_sudoku):
            wire = circuit.validate_wires(row)
            assert wire.value == 0

    def test_valid_sudoku(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        valid = circuit.is_valid2()
        for wire in valid:
            assert wire.value == 0

    def test_invalid_sudoku(self):
        circuit = self.sudoku_circuit
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        solved_sudoku[0][0] = solved_sudoku[0][1]

        circuit.commit_sudoku(solved_sudoku)

        valid = circuit.is_valid2()
        for wire in valid:
            assert not wire.value == 0
