import unittest
from mcl import Fr, G1
from NodeRingProver import NodeRingProver
from NodeType import NodeType


class TestNodeRingProver(unittest.TestCase):

    def setUp(self):
        # Set up a common environment for all tests
        self.g__ = G1.hashAndMapTo(b"setting the group generator <g>")
        self.prover = NodeRingProver(self.g__)
        self.sample_message = b'test message'
        self.sample_private_key = Fr.rnd()
        self.sample_public_keys = [self.g__ * Fr.rnd() for _ in range(5)]  # 5 sample public keys

    def test_nr_sign(self):
        signature = self.prover.nr_sign(self.sample_message, self.sample_private_key, self.sample_public_keys)
        self.assertTrue(isinstance(signature, tuple))
        self.assertEqual(len(signature), 4)
        self.assertTrue(isinstance(signature[0], G1))
        self.assertTrue(isinstance(signature[1], list))
        self.assertTrue(isinstance(signature[2], Fr))
        self.assertTrue(isinstance(signature[3], list))

    def test_nr_sign_with_type(self):
        signature_with_type = self.prover.nr_sign_with_type(self.sample_message, self.sample_private_key,
                                                            self.sample_public_keys, NodeType.LEAF)
        self.assertTrue(isinstance(signature_with_type, tuple))
        self.assertEqual(len(signature_with_type), 5)
        self.assertEqual(signature_with_type[0], NodeType.LEAF)
        self.assertTrue(isinstance(signature_with_type[1], G1))
        self.assertTrue(isinstance(signature_with_type[2], list))
        self.assertTrue(isinstance(signature_with_type[3], Fr))
        self.assertTrue(isinstance(signature_with_type[4], list))

    def test_generate_pairwise_different_random_values(self):
        random_values = NodeRingProver.generate_pairwise_different_random_values(5)
        self.assertEqual(len(random_values), 5)

        # Ensure values are pairwise different
        unique_values = set()
        for value in random_values:
            self.assertNotIn(value.getStr(), unique_values)  # Check if the value is not already in unique_values
            unique_values.add(value.getStr())  # Add the value to unique_values



if __name__ == '__main__':
    unittest.main()
