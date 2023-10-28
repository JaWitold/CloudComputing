import sys

from mcl import Fr, G1
from PKI import PKI
from NodeType import NodeType
from NodeRingProver import NodeRingProver
from NodeRingVerifier import NodeRingVerifier

sys.path.insert(1, '/home/jawitold/mcl')

if __name__ == "__main__":
    g__ = G1.hashAndMapTo(b"setting the group generator <g>")
    num_required_keys = 10

    pki = PKI()
    if pki.get_number_of_keys() < num_required_keys:
        pki.fill_database_with_keys(num_required_keys - pki.get_number_of_keys())

    y__ = pki.get_public_keys(g__, num_required_keys)

    a_ = Fr.rnd()

    prover = NodeRingProver(g__)
    verifier = NodeRingVerifier(g__)

    # Sample nr_signature verification
    signature = prover.nr_sign(b'message', a_, y__)
    print(verifier.nr_verify(b'message', signature))

    # Sample hierarchical verification (for demonstration purposes)
    leaf_signature = prover.nr_sign_with_type(b'message', a_, y__, NodeType.LEAF)
    print(verifier.hier_verify(b'messagae', leaf_signature, y__))
