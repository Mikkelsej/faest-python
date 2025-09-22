import pytest
from main import ExtensionField

class TestExtensionField:
    def setup_method(self):
        self.field = ExtensionField(8)
    
    def teardown_method(self):
        pass
    
    def test_bitRec_numDec(self):
        for d in range(5):
            for i in range(2**d):
                bitDec = self.field.BitDec(i, d)
                numRec = self.field.NumRec(d, bitDec)
                assert numRec == i
    
    def test_add(self):
        a = 0b111   # 7
        b = 0b111   # 7
        assert self.field.add(a, b) == 0
        a = 0b100   # 4
        b = 0b011   # 3
        assert self.field.add(a, b) == 0b111   # 7

    def test_mul_in_gf3(self):
        tempField = ExtensionField(3)
        a = 0b101   # x^2 + 1
        b = 0b111   # x^2 + x + 1
        result = tempField.mul(a, b)
        # Expected: 0b110 = x^2 + x
        assert result == 0b110
    
    def test_mul_in_gf8(self):
        a = 0x53
        b = 0xCA
        result = self.field.mul(a, b)
        # Expected is 1
        assert result == 1

    def test_inverse(self):
        a = 0x53
        inv_a = self.field.inv(a)
        
        assert inv_a == 0xCA

        product = self.field.mul(a, inv_a)
        # Multiplicative identity is 1
        assert product == 1
