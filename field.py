import random


class ExtensionField:

    _irreducible = {
        3: 0b1011,
        8: 0b100011011,  # x^8 + x^4 + x^3 + x + 1
    }

    def __init__(self, m: int) -> None:
        # p^m
        self.p = 2
        self.m = m
        if not m in [3, 8, 64, 128, 192, 256, 384, 576, 768]:
            raise Exception(f"m must be one of {[8, 64, 128, 192, 256, 384, 576, 768]}")
        self.irrPoly = self._irreducible[self.m]

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def sub(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        result = 0
        while b:
            if b & 1:
                result ^= a
            b >>= 1
            a <<= 1
            if a >> self.m:
                a ^= self.irrPoly
        return result

    def inv(self, a: int) -> int:
        return self.pow(a, (1 << self.m) - 2)

    def pow(self, a: int, n: int) -> int:
        result = 1
        base = a
        while n:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def bit_dec(self, i: int, d: int) -> list[int]:
        b = [0] * (d)
        for j in range(d):
            b[j] = i % 2
            i = (i - b[j]) // 2
        return b

    def num_rec(self, d: int, b: list[int]) -> int:
        result = 0
        for j in range(d):
            result += b[j] * 2**j
        return result

    def get_random(self) -> int:
        return random.randint(0, 2 ** (self.m) - 1)

    def get_random_bit(self) -> int:
        return random.randint(0, 1)
