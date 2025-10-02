from extensionfield import ExtensionField


class Verifier:
    def __init__(self, field: ExtensionField) -> None:
        self.field: ExtensionField = field
        self.delta: int
        self.q: list[int]
        self.index: int = 0


    def setDelta(self, delta: int) -> None:
        self.delta = delta


    def setQ(self, q: list[int]) -> None:
        self.q = q


    def commit(self, di: int) -> None:
        i: int = self.index
        qi: int = self.q[i] + di * self.delta
        self.q[i] = qi

        # Increase index for next vi, ui
        self.index += 1
    
    def check(self, qi: int, index: int) -> bool:
        original_qi: int = self.q[index]
        
        if original_qi == qi:
            return True

        return False
