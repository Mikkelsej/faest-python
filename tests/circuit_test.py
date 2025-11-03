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
        field = ExtensionField(8)
        vole = Vole(field, 1000)
        prover = Prover(vole)
        verifier = Verifier(vole)
        self.sudoku_circuit = SudokuCircuit(prover, verifier, vole)

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
        generator = SudokuGenerator()
        part_sudoku = generator.part_sudoku
        solved_sudoku = generator.solution
        valid_list = []
        for i, row in enumerate(part_sudoku):
            for j, value in enumerate(row):
                if value != 0:
                    solved_value = solved_sudoku[i][j]
                    valid = solved_value == value
                    valid_list.append(valid)
        assert all(valid_list)

