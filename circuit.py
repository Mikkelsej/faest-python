from vole import Vole
from prover import Prover
from verifier import Verifier


class Gate:
    """Represents a gate in the arithmetic circuit."""
    def __init__(self, gate_type, inputs, output):
        self.gate_type = gate_type  # 'ADD', 'MULT', 'CONST'
        self.inputs = inputs  # list of Wire objects
        self.output = output  # Wire object

    def evaluate(self):
        """Evaluate the gate based on input values."""
        if self.gate_type == 'CONST':
            return self.output.value
        elif self.gate_type == 'ADD':
            return sum(w.value for w in self.inputs)
        elif self.gate_type == 'MULT':
            result = 1
            for w in self.inputs:
                result *= w.value
            return result
        else:
            raise ValueError(f"Unknown gate type: {self.gate_type}")

class Wire:
    """Represents a wire carrying a value in the circuit."""
    _id_counter = 0

    def __init__(self, value=None, name=None):
        self.value = value
        self.name = name or f"w{Wire._id_counter}"
        self.id = Wire._id_counter
        Wire._id_counter += 1

class CircuitBuilder:
    """Builds an arithmetic circuit for Sudoku verification."""

    def __init__(self):
        self.gates = []
        self.wires = []
        self.constraints = []

    def create_wire(self, value=None, name=None):
        """Create a new wire in the circuit."""
        wire = Wire(value, name)
        self.wires.append(wire)
        return wire

    def add_gate(self, gate_type, inputs, output=None):
        """Add a gate to the circuit."""
        if output is None:
            output = self.create_wire()
        gate = Gate(gate_type, inputs, output)
        self.gates.append(gate)
        return output

    def add_constant(self, value):
        """Add a constant wire to the circuit."""
        wire = self.create_wire(value, f"const_{value}")
        gate = Gate('CONST', [], wire)
        self.gates.append(gate)
        return wire

    def check_range(self, wire, min_val=1, max_val=9):
        """Add constraint: min_val <= wire.value <= max_val."""
        self.constraints.append(('RANGE', wire, min_val, max_val))

    def check_all_different(self, wires):
        """Add constraint: all wires must have different values."""
        self.constraints.append(('ALL_DIFF', wires))

    def build_sudoku_circuit(self, sudoku_grid):
        """
        Build circuit for 9x9 Sudoku verification.
        sudoku_grid: 9x9 list of lists with values 1-9
        """
        # Create wires for all cells
        cell_wires = []
        for i in range(9):
            row = []
            for j in range(9):
                wire = self.create_wire(sudoku_grid[i][j], f"cell_{i}_{j}")
                row.append(wire)
                # Each cell must be in range [1, 9]
                self.check_range(wire, 1, 9)
            cell_wires.append(row)

        # Check all rows have unique values
        for i in range(9):
            self.check_all_different(cell_wires[i])

        # Check all columns have unique values
        for j in range(9):
            col = [cell_wires[i][j] for i in range(9)]
            self.check_all_different(col)

        # Check all 3x3 boxes have unique values
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(cell_wires[box_row*3 + i][box_col*3 + j])
                self.check_all_different(box)

        return cell_wires

    def verify_constraints(self):
        """Verify all constraints are satisfied."""
        for constraint in self.constraints:
            if constraint[0] == 'RANGE':
                _, wire, min_val, max_val = constraint
                if not (min_val <= wire.value <= max_val):
                    return False, f"Range constraint failed for {wire.name}"

            elif constraint[0] == 'ALL_DIFF':
                _, wires = constraint
                values = [w.value for w in wires]
                if len(values) != len(set(values)):
                    return False, f"All different constraint failed"

        return True, "All constraints satisfied"