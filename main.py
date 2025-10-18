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

    i, di = alice.commit([1, 0, 1])
    bob.update_q(i, di)

    wi, vi, i = alice.open(1, 0, 4)
    bob.check(wi, vi, i)


if __name__ == "__main__":
    main()
