"""Circuit builder and constraints for Sudoku over VOLE-backed arithmetic."""


class Gate:
    """Represents a gate in the arithmetic circuit."""

    def __init__(self, gate_type, inputs):
        self.gate_type = gate_type
        self.inputs: list[Wire] = inputs
        self.output: Wire

    def evaluate(self):
        """Evaluate the gate based on input values."""
        self.output = Wire(0)
        if self.gate_type == "add":
            self.output.value = sum(input_wire.value for input_wire in self.inputs)
        elif self.gate_type == "mul":
            result = 1
            for input_wire in self.inputs:
                result *= input_wire.value
            self.output.value = result
        else:
            pass
        return self.output.value


class Wire:
    """Represents a wire carrying a value in the circuit."""

    _id_counter = 1

    def __init__(self, value: int):
        self.value: int = value
        self.name = f"wire_{Wire._id_counter}"
        self.id = Wire._id_counter
        Wire._id_counter += 1


class CircuitBuilder:
    """Builds an arithmetic circuit for Sudoku verification."""

    def __init__(self):
        self.gates: list[Gate] = []
        self.wires: list[Wire] = []
        self.constraints: list[bool] = []
        self.is_valid: bool = all(self.constraints)

    def create_wire(self, value):
        """Create a new wire in the circuit."""
        wire = Wire(value)
        self.wires.append(wire)
        return wire

    def add_gate(self, gate_type, inputs):
        """Add a new gate to the circuit."""
        gate = Gate(gate_type, inputs)
        self.gates.append(gate)
        return gate

    def add_constraint(self, constraint):
        """Add a constraint to the circuit."""
        self.constraints.append(constraint)


from sudoku_generator import SudokuGenerator


class SudokuCircuit(CircuitBuilder):
    """Builds an arithmetic circuit for Sudoku verification."""

    def __init__(self):
        CircuitBuilder.__init__(self)
        self.build_circuit()

    def build_circuit(self):
        sudoku_generator = SudokuGenerator(9)
        solution = sudoku_generator.solution
        for row in solution:
            for value in row:
                self.create_wire(value)

        # Add addition gates for rows
        for i in range(9):
            row_wires = self.wires[i * 9 : (i + 1) * 9]
            sum_gate = self.add_gate("add", row_wires)
            self.add_constraint(sum_gate.evaluate() == 45)

        # Add addition gates for columns
        for j in range(9):
            col_wires = [self.wires[i * 9 + j] for i in range(9)]
            sum_gate = self.add_gate("add", col_wires)
            self.add_constraint(sum_gate.evaluate() == 45)

        # Add addition gates for 3x3 subgrids
        for box_row in range(3):
            for box_col in range(3):
                box_wires = []
                for i in range(3):
                    for j in range(3):
                        box_wires.append(
                            self.wires[(box_row * 3 + i) * 9 + (box_col * 3 + j)]
                        )
                sum_gate = self.add_gate("add", box_wires)
                self.add_constraint(sum_gate.evaluate() == 45)

        print(self.is_valid)


SudokuCircuit()
