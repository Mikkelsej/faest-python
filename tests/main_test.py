import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier


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

    @pytest.mark.parametrize("iteration", range(1000))
    def test_vole(self, iteration: int) -> None:
        vole: Vole = Vole(self.field, 1000)
        alice = Prover(vole)
        bob = Verifier(vole)
        self.verifier_delta(bob)
        self.verifier_q(bob)
        self.prover_v(alice)
        self.prover_u(alice)
        self.vole_add(alice, bob)
        self.vole_mul(alice, bob)

    def verifier_delta(self, verifier: Verifier) -> None:
        delta: int = verifier.delta
        assert 0 <= delta <= 255

    def verifier_q(self, verifier: Verifier) -> None:
        q: list[int] = verifier.q
        for qi in q:
            assert 0 <= qi <= 255

    def prover_v(self, prover: Prover) -> None:
        v: list[int] = prover.v
        for vi in v:
            assert 0 <= vi <= 255

    def prover_u(self, prover: Prover) -> None:
        u: list[int] = prover.u
        for ui in u:
            assert 0 == ui or ui == 1

    def vole_add(self, prover: Prover, verifier: Verifier) -> None:
        u: list[int] = prover.u
        v: list[int] = prover.v
        q: list[int] = verifier.q
        delta: int = verifier.delta

        for index in range(len(u) - 1):
            v_prime, u_prime = prover.add(
                v[index], v[index + 1], u[index], u[index + 1]
            )

            q_prime = verifier.add(q[index], q[index + 1])

            assert q_prime == self.field.add(v_prime, u_prime * delta)

    def vole_mul(self, prover: Prover, verifier: Verifier) -> None:
        for index_a in range(len(prover.u) - 2):
            index_b = index_a + 1
            index_c, correction = prover.mul_commit(index_a, index_b)

            verifier.update_q(index_c, correction)

            d, e = prover.mul(index_a, index_b, index_c)

            assert verifier.check_mul(index_a, index_b, index_c, d, e)
