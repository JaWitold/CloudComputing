import sys

from typing import List, Tuple
from mcl import Fr, G1
from schnorr_sign import Verifier
from NodeType import NodeType

sys.path.insert(1, '/home/jawitold/mcl')


class NodeRingVerifier:
    def __init__(self, g__: G1):
        self.g__ = g__

    def hier_verify(self, m: bytes, sigma: Tuple[NodeType, G1, List[Tuple[G1, Tuple[Fr, Fr]]], Fr, List[G1]],
                    y__: List[G1]) -> bool:
        node_type, *signature = sigma

        if not self.nr_verify(m, tuple(signature)):
            return False

        if node_type == NodeType.LEAF:
            return True
        else:
            child_signatures = signature[
                -1]  # Assuming the child signatures are stored in the last element of the signature
            for child_signature, y_i__ in zip(child_signatures, y__):
                if not self.hier_verify(m, child_signature, [y_i__]):
                    return False

        return True

    def nr_verify(self, m: bytes, signature: Tuple[G1, List[Tuple[G1, Tuple[Fr, Fr]]], Fr, List[G1]]) -> bool:
        a_signature__, rs_, s_, y__ = signature
        sv = Verifier(self.g__)

        dd_ = []
        hh_ = []

        for r_i__, s_i_ in rs_:
            dd_.append(int(sv.verify(bytes(r_i__), s_i_, a_signature__)))
            h_i_ = Fr()
            h_i_.setInt(int.from_bytes(
                G1.hashAndMapTo(m + bytes(r_i__) + bytes(s_i_[0].getStr()) + bytes(s_i_[1].getStr())).getStr(),
                'little'))
            hh_.append(h_i_)

        sum_t__ = G1()
        for hi_, (ri__, si_), yi__ in zip(hh_, rs_, y__):
            sum_t__ += ri__ + yi__ * hi_
        prod = True
        for d_ in dd_:
            prod = prod and d_

        return bool(self.g__ * s_ == sum_t__ and prod)
