"""Circuit builder and constraints for Sudoku over VOLE-backed arithmetic."""


from field import ExtensionField
from prover import Prover
from verifier import Verifier


class Gate:
    """Represents a gate in the arithmetic circuit."""

    def __init__(self, gate_type, inputs, prover, verifier):
        self.gate_type = gate_type
        self.inputs: list[Wire] = inputs
        self.output: Wire
        self.field: ExtensionField = ExtensionField(8)
        self.prover: Prover = prover
        self.verifier: Verifier = verifier

    def evaluate(self):
        """Evaluate the gate based on input values."""
        self.output = Wire(0)
        if self.gate_type == "add":
            result = 0
            for input_wire in self.inputs:
                result = self.field.add(result, input_wire.value)
            commitment_index = self.inputs[0].commitment_index
            for i in range(len(self.inputs) - 1):
                commitment_index = self.prover.add(commitment_index, self.inputs[i + 1].commitment_index)
                commitment_index = self.verifier.add(commitment_index, self.inputs[i + 1].commitment_index)
            self.output.value = result
            self.output.commitment_index = commitment_index

        elif self.gate_type == "mul":
            result = 1
            for input_wire in self.inputs:
                result = self.field.mul(result, input_wire.value)
            commitment_index = self.inputs[0].commitment_index
            for i in range(len(self.inputs) - 1):
                result_idx, correction, d, e = self.prover.mul(commitment_index, self.inputs[i + 1].commitment_index)
                commitment_index = self.verifier.mul(commitment_index, self.inputs[i + 1].commitment_index, correction)
            self.output.value = result
            self.output.commitment_index = commitment_index

        elif self.gate_type == "square":
            result = 1
            for input_wire in self.inputs:
                result = self.field.mul(result, self.field.mul(input_wire.value, input_wire.value))
            commitment_index = None
            for i in range(len(self.inputs)):
                square_idx, correction, d, e = self.prover.mul(self.inputs[i].commitment_index, self.inputs[i].commitment_index)
                square_commit = self.verifier.mul(self.inputs[i].commitment_index, self.inputs[i].commitment_index, correction)
                if commitment_index is None:
                    commitment_index = square_commit
                else:
                    result_idx, correction2, d2, e2 = self.prover.mul(commitment_index, square_commit)
                    commitment_index = self.verifier.mul(commitment_index, square_commit, correction2)
            self.output.value = result
            self.output.commitment_index = commitment_index

        elif self.gate_type == "cube":
            result = 1
            for input_wire in self.inputs:
                square = self.field.mul(input_wire.value, input_wire.value)
                cube = self.field.mul(square, input_wire.value)
                result = self.field.mul(result, cube)
            commitment_index = None
            for i in range(len(self.inputs)):
                square_idx, correction1, d1, e1 = self.prover.mul(self.inputs[i].commitment_index, self.inputs[i].commitment_index)
                square_commit = self.verifier.mul(self.inputs[i].commitment_index, self.inputs[i].commitment_index, correction1)

                cube_idx, correction2, d2, e2 = self.prover.mul(square_idx, self.inputs[i].commitment_index)
                cube_commit = self.verifier.mul(square_commit, self.inputs[i].commitment_index, correction2)

                if commitment_index is None:
                    commitment_index = cube_commit
                else:
                    result_idx, correction3, d3, e3 = self.prover.mul(commitment_index, cube_commit)
                    commitment_index = self.verifier.mul(commitment_index, cube_commit, correction3)
            self.output.value = result
            self.output.commitment_index = commitment_index

        elif self.gate_type == "pow":
            input_wire = self.inputs[0]
            wires: list[Wire] = [input_wire]
            for i in range(self.field.m - 1):
                gate = Gate("square", [wires[i]], self.prover, self.verifier)
                wire = Wire(gate.evaluate(), gate.output.commitment_index)
                wires.append(wire)
            output_gate = Gate("mul", wires, self.prover, self.verifier)
            self.output.value = output_gate.evaluate()
            self.output.commitment_index = output_gate.output.commitment_index

        elif self.gate_type == "check_0":
            wires: list[Wire] = []
            i, _ = self.prover.commit(1)
            wire_1 = Wire(1, i)
            for wire in self.inputs:
                gate = Gate("pow", [wire], self.prover, self.verifier)
                wire = Wire(gate.evaluate(), gate.output.commitment_index)
                wires.append(wire)

            wires_2: list[Wire] = []
            for wire in wires:
                gate = Gate("add", [wire, wire_1], self.prover, self.verifier)
                wire = Wire(gate.evaluate(), gate.output.commitment_index)
                wires_2.append(wire)

            gate = Gate("mul", wires_2, self.prover, self.verifier)
            wire = Wire(gate.evaluate(), gate.output.commitment_index)

            gate = Gate("add", [wire, wire_1], self.prover, self.verifier)
            wire = Wire(gate.evaluate(), gate.output.commitment_index)
            self.output.value = wire.value
            self.output.commitment_index = wire.commitment_index


        return self.output.value



class Wire:
    """Represents a wire carrying a value in the circuit."""

    _id_counter = 1

    def __init__(self, value: int, commitment_index: int | None = None):
        self.value: int = value
        self.name = f"wire_{Wire._id_counter}"
        self.id = Wire._id_counter
        self.commitment_index = commitment_index  # VOLE commitment index, if committed
        Wire._id_counter += 1


class CircuitBuilder:
    """Builds an arithmetic circuit for Sudoku verification."""

    def __init__(self, prover: Prover = None, verifier: Verifier = None):
        self.gates: list[Gate] = []
        self.wires: list[list[Wire]] = [[] for _ in range(9)]
        self.constraints: list[bool] = []
        self.is_valid: bool = all(self.constraints)
        self.prover = prover
        self.verifier = verifier

    def create_wire(self, value: int, i: int, j: int):
        """Create a new wire in the circuit."""
        wire = Wire(value)
        self.wires[i][j] = wire
        return wire

    def add_gate(self, gate_type, inputs):
        """Add a new gate to the circuit."""
        gate = Gate(gate_type, inputs, self.prover, self.verifier)
        self.gates.append(gate)
        return gate

    def add_constraint(self, constraint):
        """Add a constraint to the circuit."""
        self.constraints.append(constraint)