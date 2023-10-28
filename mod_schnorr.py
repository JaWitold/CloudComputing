import sys

sys.path.insert(1, '/home/jawitold/mcl')

from mcl import Fr, G1, G2, GT


class Prover:

    def __init__(self, g__: G1):
        # keygen
        a_ = Fr.rnd()
        self.a__ = g__ * a_

        self.a_ = a_
        self.g__ = g__
        self.x_ = Fr.rnd()
        self.x__ = g__ * self.x_

    def get_pk(self):
        return self.a__

    def get_x(self) -> G1:
        return self.x__

    def get_s(self, c_: Fr) -> G2:
        g___ = G2.hashAndMapTo(self.x__.getStr() + c_.getStr())
        return g___ * (self.x_ + self.a_ * c_)


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

    def verify(self, s___: G2) -> bool:
        g___ = G2.hashAndMapTo(self.x__.getStr() + self.c_.getStr())

        return GT.pairing(self.g__, s___) == GT.pairing(self.x__ + (self.a__ * self.c_), g___)


if __name__ == "__main__":
    # setup
    g__ = G1.hashAndMapTo(b"test")

    prover = Prover(g__)
    verifier = Verifier(g__, prover.get_pk())

    x__ = prover.get_x()
    verifier.set_x(x__)

    c_ = verifier.get_c()

    s___ = prover.get_s(c_)

    print(verifier.verify(s___))
