"""Circuit builder and constraints for Sudoku over VOLE-backed arithmetic."""


from field import ExtensionField


class Gate:
    """Represents a gate in the arithmetic circuit."""

    def __init__(self, gate_type, inputs):
        self.gate_type = gate_type
        self.inputs: list[Wire] = inputs
        self.output: Wire
        self.field: ExtensionField = ExtensionField(8)

    def evaluate(self):
        """Evaluate the gate based on input values."""
        self.output = Wire(0)
        if self.gate_type == "add":
            result = 0
            for input_wire in self.inputs:
                result = self.field.add(result, input_wire.value)
            self.output.value = result
        elif self.gate_type == "mul":
            result = 1
            for input_wire in self.inputs:
                result = self.field.mul(result, input_wire.value)
            self.output.value = result
        elif self.gate_type == "square":
            result = 1
            for input_wire in self.inputs:
                result = self.field.mul(input_wire.value, input_wire.value)
            self.output.value = result
        elif self.gate_type == "cube":
            result = 1
            for input_wire in self.inputs:
                square = self.field.mul(input_wire.value, input_wire.value)
                result = self.field.mul(square, input_wire.value)
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
        self.wires: list[list[Wire]] = [[] for _ in range(9)]
        self.constraints: list[bool] = []
        self.is_valid: bool = all(self.constraints)

    def create_wire(self, value, row: int):
        """Create a new wire in the circuit."""
        wire = Wire(value)
        self.wires[row].append(wire)
        return wire

    def add_gate(self, gate_type, inputs):
        """Add a new gate to the circuit."""
        gate = Gate(gate_type, inputs)
        self.gates.append(gate)
        return gate

    def add_constraint(self, constraint):
        """Add a constraint to the circuit."""
        self.constraints.append(constraint)