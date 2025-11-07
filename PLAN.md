# ZKP Sudoku Circuit Implementation Plan

## Current Status
✅ VOLE primitive working  
✅ Commit/open protocol functional  
✅ Sudoku commitment working (81 cells)  
✅ Bit-level opening verified  
✅ Constraint math proven (sum of squares + cubes)  

❌ Circuit evaluation over commitments  
❌ ZK constraint proving  
❌ Multiplication gate integration  
❌ End-to-end ZKP protocol  

---

## Step 1: Single Row Constraint Proof 🎯 **START HERE**
**Goal:** Prove one row satisfies sudoku constraints

**Implement in `sudoku_circuit.py`:**
```python
def verify_row_constraint(self, row_index: int) -> bool:
    # 1. Get row wires (already committed)
    # 2. For each wire: compute square using prover.mul_commit()
    # 3. For each wire: compute cube (square × original)
    # 4. Sum all squares using prover.add()
    # 5. Sum all cubes using prover.add()
    # 6. Verify sums match expected values with verifier.check_mul()
```

**Test in `tests/circuit_test.py`:**
- Test valid row passes
- Test invalid row fails

**Expected constants (from GF(2^8)):**
- Sum of squares (1²+2²+...+9²) = 1
- Sum of cubes (1³+2³+...+9³) = 73

---

## Step 2: Extend to All Constraints
**Implement:**
- `verify_column_constraint(col_index)` - same pattern as row
- `verify_box_constraint(box_index)` - same pattern for 3×3 boxes
- `verify_all_constraints()` - check all 27 constraints (9 rows + 9 cols + 9 boxes)

**Test:** Full sudoku constraint verification

---

## Step 3: Integrate Gates
**Update `circuit.py`:**
- Modify `Gate.evaluate()` to use VOLE operations
- Return commitment indices instead of plain values
- Add verifier-side checking

---

## Step 4: Full ZKP Protocol
**Implement in `sudoku_circuit.py`:**
```python
def prove_sudoku(self, sudoku) -> dict:
    # Returns proof transcript
    
def verify_proof(self, proof) -> bool:
    # Verifies proof
```

**Test:** End-to-end prove/verify workflow

---

## Step 5: Public Inputs
**Goal:** Handle partially filled sudoku puzzles (prover only commits unknown cells)

**Implement in `sudoku_circuit.py`:**
```python
def commit_sudoku_with_public(self, sudoku: list[list[int]], public_mask: list[list[bool]]):
    # For each cell (i, j):
    #   - If public_mask[i][j] == True: cell is public (known to verifier)
    #   - If public_mask[i][j] == False: cell is private (commit it)
    # Store public cells separately for verification
    
def verify_row_constraint_with_public(self, row_index: int) -> bool:
    # Mix public and committed values in constraint computation
    # Public values contribute directly (no VOLE operations needed)
    # Private values use mul_commit as before
```

**Public Input Handling:**
1. **Parse puzzle** - separate given cells (public) from solution cells (private)
2. **Commit only private cells** - reduces VOLE consumption from 81×8 to ~40×8 indices
3. **Verifier checks public cells** - ensures prover uses correct puzzle
4. **Constraint mixing** - combine public values + committed values in same constraint

**Test in `tests/circuit_test.py`:**
```python
def test_public_inputs(self):
    # Use self.part_sudoku as public puzzle
    # Commit only the cells that were 0 in part_sudoku
    # Verify constraints still hold
    assert circuit.verify_all_constraints() == True
```

**Benefits:**
- More realistic ZKP (prove you know solution without revealing it)
- Reduced proof size (fewer commitments)
- Matches actual sudoku puzzle scenario

---

## Step 6: Non-Interactive (Advanced)
- Fiat-Shamir transform
- Hash-based challenges
- Proof serialization

---

## Immediate Action
**Write test first:**
```python
def test_verify_row_constraint(self):
    circuit.commit_sudoku(self.solved_sudoku)
    assert circuit.verify_row_constraint(0) == True
```

**Then implement the method to make it pass.**

