import os
import random
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from field import ExtensionField
from prover import Prover
from verifier import Verifier
from vole import Vole


class TestPIT:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.field = ExtensionField(8)
        self.vole = Vole(self.field, 4000)
        self.prover = Prover(self.vole)
        self.verifier = Verifier(self.vole)

    def test_pit_field(self):
        for _ in range(1000):
            row = list(range(1, 10))  # 1..9

            # shuffle to create permutations
            random_row = row[:]
            random.shuffle(random_row)

            random_challenge = self.field.get_random()

            result_row = 1
            result_random_row = 1

            # Do a polynomial identity test
            for i in range(9):
                result_row = self.field.mul(result_row, self.field.sub(random_challenge, row[i]))
                result_random_row = self.field.mul(
                    result_random_row, self.field.sub(random_challenge, random_row[i])
                )

            # if the difference is 0, then the polynomials are probably equal
            # if not, then the polynomials are definitely different
            difference = result_random_row - result_row
            assert difference == 0

    def test_pit_field_invalid(self):
        passed_count = 0
        failed_count = 0
        for _ in range(1000):
            row = list(range(1, 10))  # 1..9

            # Create an invalid row by replacing one element with a duplicate
            # This ensures we have a different multiset
            random_row = row[:]
            random.shuffle(random_row)
            # Replace the last element with a duplicate of the first
            random_row[-1] = random_row[0]

            random_challenge = self.field.get_random()

            result_row = 1
            result_random_row = 1

            # Do a polynomial identity test
            for i in range(9):
                result_row = self.field.mul(result_row, self.field.sub(random_challenge, row[i]))
                result_random_row = self.field.mul(
                    result_random_row, self.field.sub(random_challenge, random_row[i])
                )

            difference = result_random_row - result_row
            if difference != 0:
                failed_count += 1
            else:
                passed_count += 1

        # The PIT should fail (difference != 0) in most cases
        # but can pass with probability 1/|field| when a challenge equals one of the roots
        # With 1000 iterations and field size 2^8 = 256, we expect 9/256 approximately 3% false positives
        assert failed_count > 950
