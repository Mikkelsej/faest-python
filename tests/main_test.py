import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier


class TestExtensionField(unittest.TestCase):
    def setUp(self):
        self.field = ExtensionField(8)
        self.vole = Vole(self.field, 1000)
        alice = Prover(self.vole)
        bob = Verifier(self.vole)

    def tearDown(self):
        pass

    def test_bitRec_numDec(self):
        for d in range(5):
            for i in range(2**d):
                bitDec = self.field.BitDec(i, d)
                numRec = self.field.NumRec(d, bitDec)
                assert numRec == i

    def test_add(self):
        a = 0b111  # 7
        b = 0b111  # 7
        assert self.field.add(a, b) == 0
        a = 0b100  # 4
        b = 0b011  # 3
        assert self.field.add(a, b) == 0b111  # 7

    def test_mul_in_gf3(self):
        tempField = ExtensionField(3)
        a = 0b101  # x^2 + 1
        b = 0b111  # x^2 + x + 1
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

    def test_vole(self):
        for _ in range(1000):
            vole: Vole = Vole(self.field, 1000)
            alice = Prover(vole)
            bob = Verifier(vole)
            self.verifier_delta(bob)
            self.verifier_q(bob)
            self.prover_v(alice)
            self.prover_u(alice)
            self.vole_add(alice, bob)

    def verifier_delta(self, verifier: Verifier):
        delta: int = verifier.delta
        assert 0 <= delta <= 255

    def verifier_q(self, verifier: Verifier):
        q: list[int] = verifier.q
        for qi in q:
            assert 0 <= qi <= 255


    def prover_v(self, prover: Prover):
        v: list[int] = prover.v
        for vi in v:
            assert 0 <= vi <= 255

    def prover_u(self, prover: Prover):
        u: list[int] = prover.u
        for ui in u:
            assert 0 == ui or ui == 1

    def vole_add(self, prover: Prover, verifier: Verifier):
        u: list[int] = prover.u
        v: list[int] = prover.v
        q: list[int] = verifier.q
        delta: int = verifier.delta

        for index in range(len(u)-1):
            v_prime, u_prime = prover.add(v[index], v[index+1], u[index], u[index+1])
            
            q_prime = verifier.add(q[index], q[index+1])

            assert q_prime == self.field.add(v_prime, u_prime*delta)