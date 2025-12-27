import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from circuit import Check0Gate, MulGate, NumRecGate, PowGate, Wire
from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from sudoku_validator import PITValidator
from verifier import Verifier
from vole import Vole


class TestSudokuCircuit:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.field = ExtensionField(64)
        self.vole = Vole(self.field, 100000)
        self.prover = Prover(self.vole)
        self.verifier = Verifier(self.vole)
        self.validator = PITValidator()
        self.sudoku_circuit = SudokuCircuit(self.prover, self.verifier, self.vole, self.validator)
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
        powers_to_test = [0, 1, 2, 3, 4, 5, 10, 50, 100, 500, 1000]

        for power in powers_to_test:
            val = 2
            idx, di = self.prover.commit(val)
            self.verifier.update_q(idx, di)
            wire = Wire(idx)

            expected = self.field.pow(val, power)

            result_wire = PowGate(wire, self.prover, self.verifier, power).evaluate()
            assert result_wire.get_value(self.prover) == expected

        idx, di = self.prover.commit(0)
        self.verifier.update_q(idx, di)
        wire = Wire(idx)
        result_wire = PowGate(wire, self.prover, self.verifier, 2**self.field.m - 1).evaluate()
        assert result_wire.get_value(self.prover) == 0

    def test_check_0_gate_valid(self):
        wires: list[Wire] = []
        for _ in range(10):
            idx, di = self.prover.commit(0)
            self.verifier.update_q(idx, di)
            wires.append(Wire(idx))
        result_wire = Check0Gate(wires, self.prover, self.verifier).evaluate()
        assert result_wire.get_value(self.prover) == 0

    def test_check_0_gate_invalid(self):
        wires: list[Wire] = []
        for _ in range(10):
            random_val = self.field.get_random()
            idx, di = self.prover.commit(random_val)
            self.verifier.update_q(idx, di)
            wires.append(Wire(idx))
        result_wire = Check0Gate(wires, self.prover, self.verifier).evaluate()
        assert not result_wire.get_value(self.prover) == 0

    def test_rec_gate(self):
        value = self.field.get_random()

        bits = self.field.bit_dec(value, self.field.m)
        wires = []
        for bit in bits:
            idx, di = self.prover.commit(bit)
            self.verifier.update_q(idx, di)
            wires.append(Wire(idx))

        gate = NumRecGate(wires, self.prover, self.verifier)
        wire = gate.evaluate()
        assert wire.get_value(self.prover) == value

    def test_valid_sudoku(self):
        circuit = self.sudoku_circuit

        circuit.commit_sudoku(self.solved_sudoku)
        result = circuit.is_valid()
        assert result

    def test_invalid_sudoku(self):
        circuit = self.sudoku_circuit
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        solved_sudoku[0][0] = solved_sudoku[0][1]

        circuit.commit_sudoku(solved_sudoku)

        result = circuit.is_valid()
        assert not result

    @pytest.mark.parametrize("iteration", range(20))
    def test_multiple_random_valid_sudokus(self, iteration):
        generator = SudokuGenerator()
        solved_sudoku = generator.solution

        vole = Vole(self.field, 20000)
        prover = Prover(vole)
        verifier = Verifier(vole)
        circuit = SudokuCircuit(prover, verifier, vole, self.validator)

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        assert result, f"Random sudoku #{iteration + 1} failed validation"

    def test_known_valid_sudoku_1(self):
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
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    def test_known_valid_sudoku_2(self):
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
            [9, 1, 2, 3, 4, 5, 6, 7, 8],
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    def test_known_valid_sudoku_3(self):
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
            [2, 3, 9, 8, 4, 1, 5, 6, 7],
        ]

        circuit.commit_sudoku(known_sudoku)
        result = circuit.is_valid()
        assert result

    @pytest.mark.parametrize("iteration", range(10))
    def test_invalid_sudokus(self, iteration):
        vole1 = Vole(self.field, 4000)
        prover1 = Prover(vole1)
        verifier1 = Verifier(vole1)
        circuit1 = SudokuCircuit(prover1, verifier1, vole1, self.validator)
        assert not self.invalid_sudoku_duplicate_in_column(circuit1)

        vole2 = Vole(self.field, 4000)
        prover2 = Prover(vole2)
        verifier2 = Verifier(vole2)
        circuit2 = SudokuCircuit(prover2, verifier2, vole2, self.validator)
        assert not self.invalid_sudoku_duplicate_in_box(circuit2)

        vole3 = Vole(self.field, 4000)
        prover3 = Prover(vole3)
        verifier3 = Verifier(vole3)
        circuit3 = SudokuCircuit(prover3, verifier3, vole3, self.validator)
        assert self.all_rows_columns_boxes_individually(circuit3, prover3)

    def invalid_sudoku_duplicate_in_column(self, circuit):
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        solved_sudoku[0][0] = solved_sudoku[1][0]

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        return result

    def invalid_sudoku_duplicate_in_box(self, circuit):
        solved_sudoku = [row[:] for row in self.solved_sudoku]
        solved_sudoku[1][1] = solved_sudoku[0][0]

        circuit.commit_sudoku(solved_sudoku)
        result = circuit.is_valid()
        return result

    def all_rows_columns_boxes_individually(self, circuit, prover):
        circuit.commit_sudoku(self.solved_sudoku)

        for i in range(9):
            row_wires = circuit.get_row_wires(i)
            wire = circuit.validate_wires(row_wires)
            if wire.get_value(prover) != 0:
                return False

        for i in range(9):
            col_wires = circuit.get_column_wires(i)
            wire = circuit.validate_wires(col_wires)
            if wire.get_value(prover) != 0:
                return False

        for i in range(9):
            box_wires = circuit.get_box_wires(i)
            wire = circuit.validate_wires(box_wires)
            if wire.get_value(prover) != 0:
                return False

        return True

    def test_cheating_prover_fails(self):
        class CheatingProver(Prover):
            def mul(self, a, b):
                c, correction, d, e = super().mul(a, b)
                return c, correction, d + 1, e

        cheating_prover = CheatingProver(self.vole)

        idx1, di1 = cheating_prover.commit(2)
        self.verifier.update_q(idx1, di1)
        wire1 = Wire(idx1)

        idx2, di2 = cheating_prover.commit(3)
        self.verifier.update_q(idx2, di2)
        wire2 = Wire(idx2)

        gate = MulGate([wire1, wire2], cheating_prover, self.verifier)

        with pytest.raises(Exception, match="Verification failed"):
            gate.evaluate()
