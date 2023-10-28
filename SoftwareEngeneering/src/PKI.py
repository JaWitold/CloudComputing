import sqlite3
from typing import List, Sequence
from mcl import G1, Fr


class PKI:
    def __init__(self, db_name="pki_database.db"):
        self.conn = sqlite3.connect(db_name)
        self._initialize_database()

    def _initialize_database(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS keys (
                    id INTEGER PRIMARY KEY,
                    private_key TEXT NOT NULL
                )
            """)

    def store_private_key(self, private_key_: Fr):
        with self.conn:
            self.conn.execute("""
                INSERT INTO keys (private_key) VALUES (?)
            """, (private_key_.getStr(),))

    def get_public_keys(self, generator__: G1, n: int = -1) -> List[G1]:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT private_key FROM keys LIMIT ?
            """, (n,))
            private_keys = [self._deserialize_fr(private_key_[0]) for private_key_ in cursor.fetchall()]
            return [generator__ * private_key_ for private_key_ in private_keys]

    def get_public_keys_by_indexes(self, generator__: G1, indexes: Sequence[int]) -> List[G1]:
        with self.conn:
            cursor = self.conn.execute(f"""
                SELECT private_key FROM keys WHERE id IN ({','.join('?' for _ in indexes)})
            """, indexes)
            private_keys = [self._deserialize_fr(private_key_[0]) for private_key_ in cursor.fetchall()]
            return [generator__ * private_key_ for private_key_ in private_keys]

    def _deserialize_fr(self, data: bytes) -> Fr:
        fr_obj = Fr()
        fr_obj.setStr(data)
        return fr_obj

    def fill_database_with_keys(self, n: int):
        for _ in range(n):
            private_key_ = Fr.rnd()
            self.store_private_key(private_key_)

    def get_number_of_keys(self) -> int:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT COUNT(*) FROM keys
            """)
            return cursor.fetchone()[0]


# Sample usage:
if __name__ == "__main__":
    g__ = G1.hashAndMapTo(b"setting the group generator <g>")
    pki = PKI()
    pki.fill_database_with_keys(10)
    indexes = [1, 3, 5, 7]
    print(pki.get_public_keys_by_indexes(g__, indexes))  # Get the public keys by the specified indexes
