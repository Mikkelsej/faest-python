from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from sudoku_validator import Check0Validator, SudokuValidator, PITValidator
from verifier import Verifier
from vole import Vole

def get_index(validator: SudokuValidator):
    vole_length: int = 50000
    total_length: int = 100000
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, vole_length, total_length)

    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)

    solved_sudoku = SudokuGenerator().solution

    circuit = SudokuCircuit(alice, bob, vole, validator)

    circuit.commit_sudoku(solved_sudoku)
    valid = circuit.is_valid()
    return (alice.vole_index, alice.temp_index - vole_length), valid

def main():
    check0_validator = Check0Validator()
    pit_validator = PITValidator()

    check0_stats, check0_valid = get_index(check0_validator)
    pit_stats, pit_valid = get_index(pit_validator)


    print(f"Check0 Method used {check0_stats[0]} fresh VOLEs + {check0_stats[1]} temp storage. Valid: {check0_valid}")

    print(f"PIT Method used {pit_stats[0]} fresh VOLEs + {pit_stats[1]} temp storage. Valid: {pit_valid}")

if __name__ == "__main__":
    main()
