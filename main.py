"""Imports stuff"""

from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from sudoku_validator import Check0Validator, PITValidator
from verifier import Verifier
from vole import Vole


def main() -> None:
    """Does main stuff"""
    length: int = 10000
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, length)

    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)

    solved_sudoku = SudokuGenerator().solution

    circuit = SudokuCircuit(alice, bob, vole, PITValidator())

    circuit.commit_sudoku(solved_sudoku)

    print("Sudoku committed:")
    for row in circuit.input_sudoku:
        for wire in row:
            print(alice.u[wire.commitment_index], end=" ")
        print()

    print("Is valid:", circuit.is_valid())
    print("used: ", alice.index)


if __name__ == "__main__":
    main()
