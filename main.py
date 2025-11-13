"""Imports stuff"""

from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from verifier import Verifier
from vole import Vole


def main() -> None:
    """Does main stuff"""
    length: int = 1500
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, length)

    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)

    solved_sudoku = SudokuGenerator().solution

    circuit = SudokuCircuit(alice, bob, vole)

    circuit.commit_sudoku(solved_sudoku)

    print("Sudoku committed:")
    for row in circuit.input_sudoku:
        for wire in row:
            print(alice.u[wire.commitment_index], end=" ")
        print()

    print("Is valid:", circuit.is_valid())


if __name__ == "__main__":
    main()
