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
        self.build_circuit()
        self.input_sudoku: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]

    def create_wire(self, bits: list[int], i: int, j: int):
        value = self.vole.field.num_rec(4, bits)
        self.input_sudoku[i][j] = value

    def get_column_wires(self, col_index: int) -> list[Wire]:
        """Extract all wires from a specific column.

        Args:
            col_index: Column index (0-8)

        Returns:
            List of wires in the specified column
        """
        column_wires = []
        for row in self.wires:
            if col_index < len(row):
                column_wires.append(row[col_index])
        return column_wires

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
                if row_idx < len(self.wires) and col_idx < len(self.wires[row_idx]):
                    box_wires.append(self.wires[row_idx][col_idx])

        return box_wires

    def build_circuit(self):
        for row in self.wires:
            self.add_gate("square", row)
            self.add_gate("cube", row)
            self.add_gate("mul", row)


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

    for i, row in enumerate(solved_sudoku):
        for j, value in enumerate(row):
            bits = field.bit_dec(value, 4)
            d = []
            for bit in bits:
                vole_index, di = prover.commit(value)
                verifier.update_q(vole_index, di)
                d.append(di)
            circuit.create_wire(d, i, j)
        print(row)

    for row in circuit.input_sudoku:
        print(row)