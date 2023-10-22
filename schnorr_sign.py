import random
import sys
from random import shuffle

sys.path.insert(1, '/home/jawitold/mcl')

from mcl import Fr, G1

class Prover:
    def __init__(self, _g: G1):
        self.g = _g

    def sign(self, m: bytes, x: Fr):
        a = Fr.rnd()
        r = self.g * a
        h = Fr()
        h.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(r)).getStr(), 'little'))

        return r, a + x * h
class Verifier:

    def __init__(self, _g: G1):
        self.g = _g

    def verify(self, m: bytes, signature, y: G1):
        r, s = signature
        h = Fr()
        h.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(r)).getStr(), 'little'))

        return self.g * s == r + y * h

if __name__ == "__main__":
    # setup
    g = G1.hashAndMapTo(b"setting the group generator <g>")
    # keygen
    a = Fr.rnd()
    A = g * a

    # dummy public keys

    p = Prover(g)
    s = p.sign(b'message', a)
    v = Verifier(g)
    print(v.verify(b'message', s, A))
