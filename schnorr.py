import sys

sys.path.insert(1, '/home/jawitold/mcl')

from mcl import Fr, G1


class Prover:

    def __init__(self, g__: G1, a_: Fr):
        self.a_ = a_
        self.g__ = g__
        self.x_ = Fr.rnd()
        self.x__ = g__ * self.x_

    def get_x(self) -> G1:
        return self.x__

    def get_s(self, c_: Fr) -> Fr:
        return self.x_ + self.a_ * c_


class Verifier:

    def __init__(self, g__: G1, a__: G1):
        self.x__ = None
        self.c_ = None
        self.g__ = g__
        self.a__ = a__

    def set_x(self, x__: G1):
        self.x__ = x__

    def get_c(self) -> Fr:
        self.c_ = Fr.rnd()
        return self.c_

    def verify(self, s_: Fr) -> bool:
        return self.g__ * s_ == self.x__ + (self.a__ * self.c_)


if __name__ == "__main__":
    # setup
    g__ = G1.hashAndMapTo(b"test")

    # keygen
    a_ = Fr.rnd()
    a__ = g__ * a_

    p = Prover(g__, a_)
    v = Verifier(g__, a__)

    v.set_x(p.get_x())
    print(v.verify(p.get_s(v.get_c())))
