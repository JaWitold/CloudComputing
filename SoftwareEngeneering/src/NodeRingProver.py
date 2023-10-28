import sys
import random

from typing import List, Tuple, Optional
from mcl import Fr, G1
from schnorr_sign import Prover
from NodeType import NodeType

sys.path.insert(1, '/home/jawitold/mcl')


class NodeRingProver:
    def __init__(self, g__: G1):
        self.g__ = g__

    def nr_sign_with_type(self, m: bytes, x_: Fr, y__: List[G1], node_type: NodeType) \
            -> Tuple[NodeType, G1, List[Tuple[G1, Tuple[Fr, Fr]]], Fr, List[G1]]:
        a__, rs, s_, y_ext__ = self.nr_sign(m, x_, y__)
        return node_type, a__, rs, s_, y_ext__

    def nr_sign(self, m: bytes, x_: Fr, y__: List[G1]) -> Tuple[G1, List[Tuple[G1, Tuple[Fr, Fr]]], Fr, List[G1]]:
        a_new_ = Fr.rnd()
        a_new__ = self.g__ * a_new_
        sp = Prover(self.g__)

        aa_ = self.generate_pairwise_different_random_values(len(y__))
        rr__ = [self.g__ * a_i_ for a_i_ in aa_]
        ss_ = [sp.sign(bytes(r_i__), a_new_) for r_i__ in rr__]
        hh__ = [G1.hashAndMapTo(m + bytes(r_i__) + bytes(s_i_[0].getStr()) + bytes(s_i_[1].getStr())) for r_i__, s_i_ in
                zip(rr__, ss_)]

        temp__ = G1()
        p_ = Fr()
        for y_i__, h_i__ in zip(y__, hh__):
            p_.setInt(int.from_bytes(h_i__.getStr(), 'little'))
            temp__ = temp__ + y_i__ * -p_
        while True:
            ax_ = Fr.rnd()
            cond = False
            rx__ = self.g__ * ax_ + temp__

            for r_i__ in rr__:
                if rx__ == r_i__:
                    cond = True
                    break
            if not rx__.isZero() and not cond:
                break
        sx_ = sp.sign(bytes(rx__), a_new_)

        hx_ = Fr()
        hx_.setInt(
            int.from_bytes(G1.hashAndMapTo(m + bytes(rx__) + bytes(sx_[0].getStr()) + bytes(sx_[1].getStr())).getStr(),
                           'little'))

        s_ = Fr()
        for a_i_ in aa_:
            s_ += a_i_
        s_ += ax_ + x_ * hx_

        index = random.randint(0, len(y__))
        rr__.insert(index, rx__)
        ss_.insert(index, sx_)
        y__.insert(index, self.g__ * x_)

        rs_ = [(r_i__, s_i_) for r_i__, s_i_ in zip(rr__, ss_)]

        return a_new__, rs_, s_, y__

    @staticmethod
    def generate_pairwise_different_random_values(n: int, random_values_: Optional[List[Fr]] = None) -> List[Fr]:
        if random_values_ is None:
            random_values_ = []
        while len(random_values_) < n:
            random_value_ = Fr.rnd()
            try:
                random_values_.index(random_value_)
            except:
                random_values_.append(random_value_)
        return random_values_
