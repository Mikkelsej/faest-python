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
                print(bitDec, numRec)
                assert numRec == i
    
    def test_add(self):
        a = [1, 1, 1]
        b = [1, 1, 1]
        assert self.field.add(a, b) == [0, 0, 0]
        a =  [0, 0, 1]
        b = [1, 1, 0]
        assert self.field.add(a,b) == [1, 1, 1]

    def test_mul_in_gf3(self):
        tempField = ExtensionField(3)
        a = [1, 0, 1]
        b = [1, 1, 1]
        assert tempField.mul(a,b) == [0,1,1]
    
    def test_mul_in_gf8(self):
        a = self.field.BitDec(0x53, 8)
        b = self.field.BitDec(0xCA, 8)
        assert self.field.mul(a,b) == [1]

    def test_inverse(self):
        a = self.field.BitDec(0x53, 8)
        inv_a = self.field.inv(a)
        
        assert self.field.NumRec(8, inv_a) == 0xCA

        product = self.field.mul(a, inv_a)

        assert product == [1]