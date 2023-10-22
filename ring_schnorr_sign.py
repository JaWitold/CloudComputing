import random
import sys
from random import shuffle

sys.path.insert(1, '/home/jawitold/mcl')

from mcl import Fr, G1


def generate_pairwise_different_random_values(n: int, random_values=None):
    if random_values is None:
        random_values = []
    while len(random_values) < n:
        random_value = Fr.rnd()
        try:
            random_values.index(random_value)
        except:
            random_values.append(random_value)
    return random_values


class Prover:
    def __init__(self, _g: G1):
        self.g = _g

    def r_sign(self, m: bytes, x: Fr, Y: list):
        """

        :param m: message in byte form
        :param x: private key
        :param Y: list of public keys excluding one matching `x`
        :return:
        """

        aa = generate_pairwise_different_random_values(len(Y))
        rr = [self.g * a_i for a_i in aa]
        hh = [G1.hashAndMapTo(m + bytes(r_i)) for r_i in rr]

        temp = G1()
        p = Fr()
        for y_i, h_i in (zip(Y, hh)):
            p.setInt(int.from_bytes(h_i.getStr(), 'little'))
            temp = temp + y_i * -p
        while True:
            ax = Fr.rnd()
            cond = False
            rx = g * ax + temp

            for r_i in rr:
                if rx == r_i:
                    cond = True
                    break
            if not rx.isZero() and not cond:
                break
        hx = Fr()
        hx.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(rx)).getStr(), 'little'))

        s = Fr()
        for a_i in aa:
            s += a_i
        s += ax + x * hx

        index = random.randint(0, len(Y))
        rr.insert(index, rx)
        Y.insert(index, g * x)

        return rr, s, Y


class Verifier:

    def __init__(self, _g: G1):
        self.g = _g

    def r_verify(self, m: bytes, signature):
        rr, s, Y = signature
        hh = []
        for r_i in rr:
            h_i = Fr()
            h_i.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(r_i)).getStr(), 'little'))
            hh.append(h_i)

        sum_t = G1()
        for hi, ri, yi in zip(hh, rr, Y):
            sum_t += ri + yi * hi
        gs = self.g * s
        res = gs == sum_t
        return res


if __name__ == "__main__":
    # setup
    g = G1.hashAndMapTo(b"setting the group generator <g>")
    # keygen
    a = Fr.rnd()
    A = g * a

    # dummy public keys
    PKI = [g * Fr.rnd() for _ in range(10)]
    shuffle(PKI)

    p = Prover(g)
    s = p.r_sign(b'message', a, PKI)
    v = Verifier(g)
    print(v.r_verify(b'message', s))
