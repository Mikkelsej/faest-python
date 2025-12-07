from field import ExtensionField
from vole import Vole
from prover import Prover
from verifier import Verifier
import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class TestVole:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.field = ExtensionField(8)

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
        self.get_random_vole()

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
        delta: int = verifier.delta

        for index_a in range(100):
            index_b: int = index_a + 1

            prover_c = prover.add(index_b, index_a)
            verifier.add(index_a, index_b)

            assert verifier.q[prover_c] == self.field.add(prover.v[prover_c], prover.u[prover_c] * delta)

    def vole_mul(self, prover: Prover, verifier: Verifier) -> None:
        for index_a in range(100):
            index_b = index_a + 1
            prover_c, correction, d, e = prover.mul(index_a, index_b)
            verifier.mul(index_a, index_b, correction)
            assert verifier.check_mul(index_a, index_b, prover_c, d, e)

    def test_commit(self):
        vole: Vole = Vole(self.field, 1000)
        prover = Prover(vole)
        verifier = Verifier(vole)

        i, di = prover.commit(1)

        verifier.update_q(i, di)

        index, wi, vi = prover.open(i)

        assert verifier.check_open(wi, vi, index)

    def get_random_vole(self):
        vole: Vole = Vole(self.field, 1000)

        delta = self.field.get_random()

        a0, a1 = vole.get_random_vole_prover()
        b = vole.get_random_vole_verifier(delta)

        assert 0 <= a0 <= 255
        assert 0 <= a1 <= 255
        assert 0 <= b <= 255

        assert b == self.field.add(a1, self.field.mul(a0, delta))
