"""Verify sudoku constraints using sum of squares and cubes for 9x9 boards"""
from field import ExtensionField
from itertools import permutations, combinations_with_replacement
from typing import Tuple
import math


def calculate_targets(n: int, field: ExtensionField) -> Tuple[int, int]:
    """Calculate target sum of squares and cubes for 1..n"""
    target_sum_sq = 0
    target_sum_cube = 0
    
    for i in range(1, n + 1):
        square = field.mul(i, i)
        target_sum_sq = field.add(target_sum_sq, square)
        cube = field.mul(square, i)
        target_sum_cube = field.add(target_sum_cube, cube)
    
    return target_sum_sq, target_sum_cube


def check_sequence(sequence, target_sq: int, target_cube: int,
                   field: ExtensionField) -> bool:
    """Check if a sequence satisfies the sum constraints"""
    sum_sq = 0
    sum_cube = 0
    
    for val in sequence:
        square = field.mul(val, val)
        sum_sq = field.add(sum_sq, square)
        cube = field.mul(square, val)
        sum_cube = field.add(sum_cube, cube)
    
    return sum_sq == target_sq and sum_cube == target_cube


def verify_sudoku_constraints(n: int, field_bits: int = 8) -> None:
    """Verify constraints for nxn sudoku"""
    field = ExtensionField(field_bits)

    target_sum_sq, target_sum_cube = calculate_targets(n, field)
    total_perms = math.factorial(n)

    # Check all permutations
    invalid_perms = 0
    for perm in permutations(range(1, n + 1)):
        if not check_sequence(perm, target_sum_sq, target_sum_cube, field):
            invalid_perms += 1
            print(f"Failed permutation: {perm}")

    # Check all non-permutation combinations
    false_positives = 0
    for combo in combinations_with_replacement(range(1, n + 1), n):
        if len(set(combo)) == n:
            continue
        if check_sequence(combo, target_sum_sq, target_sum_cube, field):
            false_positives += 1
            print(f"False positive: {combo}")

    # Results
    if invalid_perms == 0 and false_positives == 0:
        print(f"\n{n}x{n} constraints verified: all {total_perms} permutations pass, no false positives")
    else:
        print(f"\nConstraints failed:")
        if invalid_perms > 0:
            print(f"  {invalid_perms} valid permutations failed")
        if false_positives > 0:
            print(f"  {false_positives} invalid multisets passed")


def main() -> None:
    verify_sudoku_constraints(9)


if __name__ == "__main__":
    main()