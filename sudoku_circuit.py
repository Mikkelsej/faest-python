from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier
from sudoku_generator import SudokuGenerator
from circuit import CircuitBuilder, Gate, Wire


class SudokuCircuit(CircuitBuilder):
    def __init__(self, part_sudoku: list[list[int]]):
        super().__init__()
        self.create_wires(part_sudoku)
        self.build_circuit()

    def create_wires(self, part_sudoku: list[list[int]]):
        """Create wires for the given Sudoku puzzle. 0 represents empty cells."""
        for row_index, row in enumerate(part_sudoku):
            for value in row:
                if value != 0:
                    self.create_wire(value, row_index)
                else:
                    value = self.commit_value(row_index, 0)

    def commit_value(self, row: int, value: int) -> int:
        """Commit a value to a specific cell in the Sudoku puzzle."""
        wire = self.create_wire(value, row)
        return 1

    def build_circuit(self):
        for row in self.wires:
            self.add_gate("square", row)
            self.add_gate("cube", row)
            self.add_gate("mul", row)
        
        for gate in self.gates:
            print(gate.evaluate())
            
        
part_sudoku = SudokuGenerator().part_sudoku
circuit = SudokuCircuit(part_sudoku)
