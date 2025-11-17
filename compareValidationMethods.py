from field import ExtensionField
from prover import Prover
from sudoku_circuit import SudokuCircuit
from sudoku_generator import SudokuGenerator
from sudoku_validator import Check0Validator, SudokuValidator, PITValidator
from verifier import Verifier
from vole import Vole

def get_index(validator: SudokuValidator):
    length: int = 10000
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, length)

    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)

    solved_sudoku = SudokuGenerator().solution

    circuit = SudokuCircuit(alice, bob, vole, validator)

    circuit.commit_sudoku(solved_sudoku)
    circuit.is_valid()
    return alice.index

def main():
    check0_validator = Check0Validator()
    pit_validator = PITValidator()

    check0_index = get_index(check0_validator)
    pit_index = get_index(pit_validator)


    print(f"Check0 Method used {check0_index} prover indexes")

    print(f"PIT Method used {pit_index} prover indexes")

if __name__ == "__main__":
    main()
