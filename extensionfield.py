from itertools import product

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
        self.elements = [list(bits) for bits in product([0, 1], repeat=self.m)]

    def add(self, a, b):
        max_len = max(len(a),len(b))
        a = a + [0] * (max_len - len(a))
        b = b + [0] * (max_len - len(b))
        
        result = []
        for i in range(max_len):
            result.append((a[i] + b[i]) % 2)
        return result

    def sub(self, a, b):
        return self.add(a, b)

    def mul(self, a, b):
        n = len(a)
        m = len(b)

        result = [0] * (n + m - 1)  # Maximum temporary size is n+m-1
        for i in range(n):
            for j in range(m):
                result[i + j] = (result[i + j] + (a[i] * b[j])) % 2

        # Now do modulos p(x)
        result = self._mod_p(result)
        return result

    def _mod_p(self, poly: list[int]):
        modulus = self._irr_bits()
        modulus_degree = self._get_degree(modulus)
        poly = poly[:]
        while self._get_degree(poly) >= modulus_degree:
            deg_diff = self._get_degree(poly) - modulus_degree
            # shift modulus to align leading terms
            shifted_modulus = [0]*deg_diff + modulus
            # subtract (XOR for GF(2)) the shifted modulus
            poly = self.sub(poly, shifted_modulus)
            # remove trailing zeros
            while poly and poly[-1] == 0:
                poly.pop()
        
        return poly
    
    def inv(self, a):
        # Exponentiate a^(2^m - 2)
        result = [1]  # identity
        power = a[:]
        n = 2**self.m - 2

        while n:
            if n & 1:
                result = self.mul(result, power)
            power = self.mul(power, power)
            n >>= 1

        return result


    def _get_degree(self, poly):
        deg = len(poly) - 1
        while deg >= 0 and poly[deg] == 0:
            deg -= 1
        return deg

    def _irr_bits(self):
        """Return the irreducible polynomial as a little-endian bit list."""
        poly = self.irrPoly
        bits = []
        while poly > 0:
            bits.append(poly % 2)
            poly = poly // 2
        return bits

    def toField(self, x, k):
        pass

    def BitDec(self, i, d):
        b = [0] * (d)
        for j in range(d):
            b[j] = i % 2
            i = (i - b[j]) // 2
        return b

    def NumRec(self, d, b):
        result = 0
        for j in range(d):
            result += b[j] * 2**j
        return result