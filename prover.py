from extensionfield import ExtensionField


class Prover:
    def __init__(self, field: ExtensionField, length: int) -> None:
        self.field: ExtensionField = field
        self.length: int = length

        self.u: list[int]
        self.v: list[int]

        self.index: int = 0

    def setU(self, u: list[int]) -> None:
        self.u = u

    def setV(self, v: list[int]) -> None:
        self.v = v

    def commit(self, w: bytes) -> int:
        i: int = self.index
        di = self.v[i] ^ self.u[i]

        # Going to next unused vi and ui
        self.index += 1
        return di
