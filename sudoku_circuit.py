from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier
from sudoku_generator import SudokuGenerator
from circuit import CircuitBuilder, Gate, Wire


class SudokuCircuit(CircuitBuilder):
    def __init__(
        self,
        prover: Prover,
        verifier: Verifier,
        vole: Vole,
    ):
        super().__init__()
        self.prover = prover
        self.verifier = verifier
        self.vole = vole
        self.input_sudoku: list[list[Wire]] = [[Wire(0) for _ in range(9)] for _ in range(9)]

    def create_wire(self, bits: list[int], i: int, j: int, commitment_index: int):
        value = self.vole.field.num_rec(self.vole.field.m, bits)
        wire = Wire(value, commitment_index)
        self.input_sudoku[i][j] = wire

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
                bits = self.vole.field.bit_dec(value, self.vole.field.m)
                d = []
                vole_indexes = []
                for bit in bits:
                    vole_index, di = self.prover.commit(bit)
                    vole_indexes.append(vole_index)
                    self.verifier.update_q(vole_index, di)
                    d.append(di)
                vole_index = vole_indexes[0]
                self.create_wire(bits, i, j, vole_index)

    def validate_wires(self, wires: list[Wire]) -> Wire:
        squared_wires = []
        cubed_wires = []
        for wire in wires:
            square_gate = Gate("square", [wire], self.prover, self.verifier)
            square_value = square_gate.evaluate()
            squared_wires.append(Wire(square_value, square_gate.output.commitment_index))

            cube_gate = Gate("cube", [wire], self.prover, self.verifier)
            cube_value = cube_gate.evaluate()
            cubed_wires.append(Wire(cube_value, cube_gate.output.commitment_index))

        add_gate_square = Gate("add", squared_wires, self.prover, self.verifier)
        result_square = add_gate_square.evaluate()
        result_square_wire = Wire(result_square, add_gate_square.output.commitment_index)
        expected_value_of_squares = 1

        # Commit the constant value
        const_index_1, _ = self.prover.commit(expected_value_of_squares)
        wire_1 = Wire(expected_value_of_squares, const_index_1)

        result1_gate = Gate("add", [result_square_wire, wire_1], self.prover, self.verifier)
        result1_wire = Wire(result1_gate.evaluate(), result1_gate.output.commitment_index)

        add_gate_cube = Gate("add", cubed_wires, self.prover, self.verifier)
        result_cubed = add_gate_cube.evaluate()
        result_cubed_wire = Wire(result_cubed, add_gate_cube.output.commitment_index)

        expected_value_of_cubes = 73
        # Commit the constant value
        const_index_2, _ = self.prover.commit(expected_value_of_cubes)
        wire_2 = Wire(expected_value_of_cubes, const_index_2)

        result2_gate = Gate("add", [result_cubed_wire, wire_2], self.prover, self.verifier)
        result2_wire = Wire(result2_gate.evaluate(), result2_gate.output.commitment_index)

        final_gate = Gate("add", [result1_wire, result2_wire], self.prover, self.verifier)
        final_wire = Wire(final_gate.evaluate(), final_gate.output.commitment_index)

        return final_wire

    def is_valid2(self):
        valid_list = []
        for i in range(9):
            row = self.get_row_wires(i)
            valid = self.validate_wires(row)
            valid_list.append(valid)

            col = self.get_column_wires(i)
            valid = self.validate_wires(col)
            valid_list.append(valid)

            box = self.get_box_wires(i)
            valid = self.validate_wires(box)
            valid_list.append(valid)
        return valid_list


if __name__ == "__main__":
    field = ExtensionField(8)
    vole_length = 1000
    vole = Vole(field, vole_length)
    sudoku = SudokuGenerator()
    prover = Prover(vole)
    verifier = Verifier(vole)

    part_sudoku = sudoku.part_sudoku

    circuit = SudokuCircuit(prover, verifier, vole)

    solved_sudoku = sudoku.solution

    circuit.commit_sudoku(solved_sudoku)

    for row in circuit.input_sudoku:
        for wire in row:
            pass
            print(wire.value, end=" ")
        print()

    wires = circuit.get_column_wires(0)
    for wire in wires:
        print(wire.value)
