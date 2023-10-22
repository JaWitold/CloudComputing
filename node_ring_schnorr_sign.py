import random
import sys
from random import shuffle

from schnorr_sign import Prover as SProover, Verifier as SVerifier
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

    def nr_sign(self, m: bytes, x: Fr, Y: list):
        """

        :param m: message in byte form
        :param x: private key
        :param Y: list of public keys excluding one matching `x`
        :return:
        """

        a = Fr.rnd()
        A = self.g * a

        sp = SProover(self.g)

        aa = generate_pairwise_different_random_values(len(Y))
        rr = [self.g * a_i for a_i in aa]
        ss = [sp.sign(bytes(r_i), a) for r_i in rr]
        hh = [G1.hashAndMapTo(m + bytes(r_i) + bytes(s_i[0].getStr()) + bytes(s_i[1].getStr())) for r_i, s_i in zip(rr, ss)]

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
        sx = sp.sign(bytes(rx), a)

        hx = Fr()
        hx.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(rx) + bytes(sx[0].getStr()) + bytes(sx[1].getStr())).getStr(), 'little'))

        s = Fr()
        for a_i in aa:
            s += a_i
        s += ax + x * hx

        index = random.randint(0, len(Y))
        rr.insert(index, rx)
        ss.insert(index, sx)
        Y.insert(index, g * x)

        rs = [(r_i, s_i) for r_i, s_i in zip(rr, ss)]

        return A, rs, s, Y


class Verifier:

    def __init__(self, _g: G1):
        self.g = _g

    def nr_verify(self, m: bytes, signature):
        A, rs, s, Y = signature
        sv = SVerifier(self.g)

        dd = []
        hh = []

        for r_i, s_i in rs:
            dd.append(int(sv.verify(bytes(r_i), s_i, A)))
            h_i = Fr()
            h_i.setInt(int.from_bytes(G1.hashAndMapTo(m + bytes(r_i) + bytes(s_i[0].getStr()) + bytes(s_i[1].getStr())).getStr(), 'little'))
            hh.append(h_i)

        sum_t = G1()
        for hi, (ri, si), yi in zip(hh, rs, Y):
            sum_t += ri + yi * hi
        prod = True
        for d in dd:
            prod = prod and d

        return bool(self.g * s == sum_t and prod)


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
    s = p.nr_sign(b'message', a, PKI)
    v = Verifier(g)
    print(v.nr_verify(b'message', s))
