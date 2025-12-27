import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from field import ExtensionField


class TestExtensionField:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.field = ExtensionField(8)

    def test_bitRec_numDec(self) -> None:
        for d in range(5):
            for i in range(2**d):
                bitDec = self.field.bit_dec(i, d)
                numRec = self.field.num_rec(d, bitDec)
                assert numRec == i

    def test_add(self) -> None:
        a = 0b111  # 7
        b = 0b111  # 7
        assert self.field.add(a, b) == 0
        a = 0b100  # 4
        b = 0b011  # 3
        assert self.field.add(a, b) == 0b111  # 7

    def test_mul_in_gf3(self) -> None:
        tempField = ExtensionField(3)
        a = 0b101  # x^2 + 1
        b = 0b111  # x^2 + x + 1
        result = tempField.mul(a, b)
        # Expected: 0b110 = x^2 + x
        assert result == 0b110

    def test_mul_in_gf8(self) -> None:
        a = 0x53
        b = 0xCA
        result = self.field.mul(a, b)
        # Expected is 1
        assert result == 1

    def test_inverse(self) -> None:
        a = 0x53
        inv_a = self.field.inv(a)

        assert inv_a == 0xCA

        product = self.field.mul(a, inv_a)
        # Multiplicative identity is 1
        assert product == 1
