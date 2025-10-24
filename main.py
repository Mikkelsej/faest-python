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


if __name__ == "__main__":
    main()
