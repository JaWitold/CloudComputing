import unittest
from mcl import G1, Fr
from PKI import PKI


class TestPKI(unittest.TestCase):

    def setUp(self):
        # This creates an in-memory database, which is isolated from file system.
        # Useful for unit tests, as changes are not persistent.
        self.pki = PKI(":memory:")
        self.g__ = G1.hashAndMapTo(b"testing group generator")

    def test_store_private_key(self):
        initial_count = self.pki.get_number_of_keys()
        private_key_ = Fr.rnd()
        self.pki.store_private_key(private_key_)
        self.assertEqual(self.pki.get_number_of_keys(), initial_count + 1)

    def test_get_public_keys(self):
        n = 5
        self.pki.fill_database_with_keys(n)
        public_keys = self.pki.get_public_keys(self.g__, n)
        self.assertEqual(len(public_keys), n)

    def test_get_public_keys_by_indexes(self):
        n = 10
        indexes = [2, 4, 6]
        self.pki.fill_database_with_keys(n)
        public_keys = self.pki.get_public_keys_by_indexes(self.g__, indexes)
        self.assertEqual(len(public_keys), len(indexes))

    def test_fill_database_with_keys(self):
        n = 7
        self.pki.fill_database_with_keys(n)
        self.assertEqual(self.pki.get_number_of_keys(), n)

    def test_get_number_of_keys(self):
        n = 5
        self.pki.fill_database_with_keys(n)
        self.assertEqual(self.pki.get_number_of_keys(), n)


if __name__ == '__main__':
    unittest.main()
