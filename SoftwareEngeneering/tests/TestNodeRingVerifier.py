import unittest

from mcl import Fr, G1
from NodeRingProver import NodeRingProver
from NodeRingVerifier import NodeRingVerifier
from NodeType import NodeType


class TestNodeRingVerifier(unittest.TestCase):

    def setUp(self):
        self.g__ = G1.hashAndMapTo(b"setting the group generator <g>")
        self.prover = NodeRingProver(self.g__)
        self.verifier = NodeRingVerifier(self.g__)
        self.sample_message = b'sample_message'
        self.sample_private_key = Fr.rnd()
        self.sample_public_keys = [self.g__ * Fr.rnd() for _ in range(5)]

    def test_nr_verify_valid_signature(self):
        signature = self.prover.nr_sign(self.sample_message, self.sample_private_key, self.sample_public_keys)
        self.assertTrue(self.verifier.nr_verify(self.sample_message, signature))

    def test_nr_verify_invalid_signature(self):
        # Modify the signature to make it invalid
        _, rs_, s_, y__ = self.prover.nr_sign(self.sample_message, self.sample_private_key, self.sample_public_keys)
        modified_signature = self.g__, rs_, s_, y__
        self.assertFalse(self.verifier.nr_verify(self.sample_message, modified_signature))

    def test_hier_verify_valid_signature(self):
        leaf_signature = self.prover.nr_sign_with_type(self.sample_message, self.sample_private_key,
                                                       self.sample_public_keys, NodeType.LEAF)
        self.assertTrue(self.verifier.hier_verify(self.sample_message, leaf_signature, self.sample_public_keys))

    def test_hier_verify_invalid_signature(self):
        t, _, rs_, s_, y__ = self.prover.nr_sign_with_type(self.sample_message, self.sample_private_key,
                                                           self.sample_public_keys, NodeType.LEAF)
        # Modify the signature to make it invalid
        modified_signature = t, self.g__, rs_, s_, y__
        self.assertFalse(
            self.verifier.hier_verify(self.sample_message, modified_signature, self.sample_public_keys))

    # Add more test cases, especially edge cases, as needed.


if __name__ == '__main__':
    unittest.main()
