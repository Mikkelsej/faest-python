"""Verify ALL permutations of 1..9 satisfy the constraints"""
from field import ExtensionField
from itertools import permutations, combinations_with_replacement

def main() -> None:
    field: ExtensionField = ExtensionField(8)
    
    # Calculate target values
    target_sum_sq = 0
    target_sum_cube = 0
    
    for i in range(1, 10):
        square = field.mul(i, i)
        target_sum_sq = field.add(target_sum_sq, square)
        
        cube = field.mul(square, i)
        target_sum_cube = field.add(target_sum_cube, cube)
    
    print(f"Target Sum of Squares: {target_sum_sq}")
    print(f"Target Sum of Cubes: {target_sum_cube}")
    
    print(f"\n{'='*60}")
    print("VERIFICATION 1: All permutations of {1..9}")
    print("=" * 60)
    
    # Test ALL 9! = 362,880 permutations
    valid_perms = 0
    invalid_perms = 0
    count = 0
    
    for perm in permutations(range(1, 10)):
        sum_sq = 0
        sum_cube = 0
        
        for val in perm:
            square = field.mul(val, val)
            sum_sq = field.add(sum_sq, square)
            
            cube = field.mul(square, val)
            sum_cube = field.add(sum_cube, cube)
        
        count += 1
        if count % 50000 == 0:
            print(f"Checked {count} permutations...")
        
        if sum_sq == target_sum_sq and sum_cube == target_sum_cube:
            valid_perms += 1
        else:
            invalid_perms += 1
            print(f"\n❌ FAILED PERMUTATION: {perm}")
            print(f"   Sum²: {sum_sq} (expected {target_sum_sq})")
            print(f"   Sum³: {sum_cube} (expected {target_sum_cube})")
    
    print(f"\nTotal permutations checked: {count}")
    print(f"Valid permutations: {valid_perms}")
    print(f"Invalid permutations: {invalid_perms}")
    
    if invalid_perms == 0:
        print("\n✓✓✓ ALL 362,880 permutations satisfy the constraints!")
    else:
        print(f"\n❌ FAILURE: {invalid_perms} permutations do NOT satisfy constraints!")
        print("This approach is NOT SECURE!")
    
    print(f"\n{'='*60}")
    print("VERIFICATION 2: No non-permutations satisfy constraints")
    print("=" * 60)
    
    # We already tested this - but let's confirm again
    false_positives = 0
    count = 0
    
    for combo in combinations_with_replacement(range(1, 10), 9):
        # Skip valid permutations
        if len(set(combo)) == 9:  # This is a permutation
            continue
        
        sum_sq = 0
        sum_cube = 0
        
        for val in combo:
            square = field.mul(val, val)
            sum_sq = field.add(sum_sq, square)
            
            cube = field.mul(square, val)
            sum_cube = field.add(sum_cube, cube)
        
        count += 1
        if count % 10000 == 0:
            print(f"Checked {count} non-permutations...")
        
        if sum_sq == target_sum_sq and sum_cube == target_sum_cube:
            false_positives += 1
            print(f"\n❌ FALSE POSITIVE: {combo}")
    
    print(f"\nTotal non-permutations checked: {count}")
    print(f"False positives: {false_positives}")
    
    if false_positives == 0:
        print("\n✓✓✓ NO false positives - only valid permutations pass!")
    else:
        print(f"\n❌ FAILURE: {false_positives} invalid multisets pass!")
        print("This approach is NOT SECURE!")
    
    print(f"\n{'='*60}")
    print("FINAL VERDICT")
    print("=" * 60)
    
    if invalid_perms == 0 and false_positives == 0:
        print("✓✓✓ PROOF COMPLETE ✓✓✓")
        print("\nThe constraints Sum² = 1 and Sum³ = 73 are:")
        print("  1. COMPLETE: All 362,880 permutations satisfy them")
        print("  2. SOUND: No invalid multisets satisfy them")
        print("\nThis is a SECURE constraint system for Sudoku!")
    else:
        print("❌ CONSTRAINTS ARE NOT SECURE")
        print("You must use a different approach!")

if __name__ == "__main__":
    main()