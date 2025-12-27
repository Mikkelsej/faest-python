"""Imports stuff"""

from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from sudoku_validator import PITValidator
from verifier import Verifier
from vole import Vole


def main() -> None:
    """Does main stuff"""
    vole_length: int = 5000
    total_length: int = 10000
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, vole_length)

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
    print(f"VOLEs used: {alice.vole_index}/{vole_length}")
    print(f"Temp storage used: {alice.temp_index - vole_length}/{total_length - vole_length}")


if __name__ == "__main__":
    main()
