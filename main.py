"""Imports stuff"""

from field import ExtensionField
from prover import Prover
from verifier import Verifier
from vole import Vole


def main() -> None:
    """Does main stuff"""
    length: int = 1000
    field: ExtensionField = ExtensionField(8)

    vole: Vole = Vole(field, length)

    alice: Prover = Prover(vole)
    bob: Verifier = Verifier(vole)

    w = 1
    i, di = alice.commit(w)
    bob.update_q(i, di)

    wi, vi, i = alice.open(w, alice.v[0], 0)
    print(bob.check(wi, vi, i))
    value = 1
    result = 0
    for i in range(1, 10):
        square = field.mul(i, i)
        result = field.add(result, square)
    result = field.add(value, result)
    result1 = result

    value = 73
    result = 0
    for i in range(1, 10):
        square = field.mul(field.mul(i, i), i)
        result = field.add(result, square)
    result = field.add(value, result)
    result2 = result
    print(field.add(result1, result2))


if __name__ == "__main__":
    main()
