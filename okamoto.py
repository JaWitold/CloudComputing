import sys

from typing import Tuple
from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


class Prover:
    def __init__(self, g1__: G1, g2__: G1, a1_: Fr, a2_: Fr, a__: G1):
        self.x1_ = Fr()
        self.x2_ = Fr()

        self.g1__ = g1__
        self.g2__ = g2__
        self.a1_ = a1_
        self.a2_ = a2_
        self.a__ = a__

    def get_x__(self) -> G1:
        self.x1_ = Fr.rnd()
        self.x2_ = Fr.rnd()
        return (self.g1__ * self.x1_) + (self.g2__ * self.x2_)

    def get_s1_s2_(self, c_: Fr) -> Tuple[Fr, Fr]:
        return self.x1_ + (self.a1_ * c_), self.x2_ + (self.a2_ * c_)


class Verifier:
    def __init__(self, g1__: G1, g2__: G1, a__: G1):
        self.x__ = G1()
        self.c_ = Fr()

        self.g1__ = g1__
        self.g2__ = g2__
        self.a__ = a__

    def set_x__(self, x__: G1) -> None:
        self.x__ = x__

    def get_c_(self) -> Fr:
        self.c_ = Fr.rnd()
        return self.c_

    def verify(self, s: Tuple[Fr, Fr]) -> bool:
        s1_, s2_ = s
        left__ = (self.g1__ * s1_) + (self.g2__ * s2_)
        right__ = self.x__ + (self.a__ * self.c_)
        return left__ == right__


if __name__ == "__main__":
    seed = b'test'
    g1__ = G1().hashAndMapTo(seed)
    g2__ = G1().hashAndMapTo(seed)

    a1_ = Fr.rnd()
    a2_ = Fr.rnd()

    a__ = (g1__ * a1_) + (g2__ * a2_)

    prover = Prover(g1__, g2__, a1_, a2_, a__)
    verifier = Verifier(g1__, g2__, a__)

    x__ = prover.get_x__()
    verifier.set_x__(x__)

    c_ = verifier.get_c_()

    s = prover.get_s1_s2_(c_)
    print(verifier.verify(s))
