import sys
sys.path.insert(1, '/home/jawitold/mcl')

from mcl import Fr, G1

class Prover:

    def __init__(self, g: G1, a: Fr):
        self.a = a
        self.g = g
        self.x = Fr.rnd()
        self.X = g * self.x

    def get_X(self):
        return self.X

    def get_s(self, c: Fr):
        return self.x + self.a * c

class Verifier:

    def __init__(self, g: G1, A: G1):
        self.X = None
        self.c = None
        self.g = g
        self.A = A

    def set_X(self, X: G1):
        self.X = X

    def get_c(self):
        self.c = Fr.rnd()
        return self.c

    def verify(self, s: G1):
        return self.g * s == self.X + (self.A * self.c)

if __name__ == "__main__":
    # setup
    g = G1.hashAndMapTo(b"test")

    # keygen
    a = Fr.rnd()
    A = g * a

    p = Prover(g, a)
    v = Verifier(g, A)

    v.set_X(p.get_X())
    print(v.verify(p.get_s(v.get_c())))
