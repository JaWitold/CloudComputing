import json
import sys
from typing import List, Tuple, Any, Union

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


def custom_encoder(obj: Any) -> Union[str, bytes]:
    if hasattr(obj, 'getStr'):
        return obj.getStr()
    elif isinstance(obj, bytes):
        return obj.decode('latin-1')
    raise TypeError("Object of unsupported type")


def save_to_json(file_path: str, value: Any) -> None:
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(value, default=custom_encoder))


def load_from_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)


class Client:
    index: int = 0
    def __init__(self, seed: bytes, index: int) -> None:
        self.g__ = G1.hashAndMapTo(seed)
        self.alpha = Fr()
        self.index = index

    def get_w(self, rand__: list[G1]) -> G1:
        self.alpha = Fr.rnd()
        return rand__[self.index] * self.alpha

    def decode(self, ciphertexts: list[tuple[bytes | bytearray | memoryview, bytes]]):
        iv, ciphertext = ciphertexts[self.index]
        cipher = AES.new(((self.g__ * self.alpha).getStr())[:16], AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return pt.decode()
class Cloud:
    def __init__(self, g__: G1, messages: list[str]) -> None:
        self.g__ = g__
        self.messages = messages
        self.rand_ = [Fr.rnd() for _ in messages]
        self.rand__ = [self.g__ * rand_ for rand_ in self.rand_]

    def get_keys(self, w__: G1) -> list[bytes]:
        neutral_element = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
        return [((w__ * (neutral_element / rand_)).getStr())[:16] for rand_ in self.rand_]

    def encode(self, keys: list[bytes]) -> list[tuple[bytes | bytearray | memoryview, bytes]]:
        ciphertexts = []
        for key, message in zip(keys, self.messages):
            cipher = AES.new(key, AES.MODE_CBC)
            ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
            ciphertexts.append((cipher.iv, ciphertext))
        return ciphertexts


def deserialize_w(data: str):
    g = G1()
    g.setStr(bytes(data, 'latin-1'))
    return g


def deserialize_keys(data):
    return [bytes(key, 'latin-1') for key in data]


def deserialize_ciphertexts(data):
    return [(bytes(iv, 'latin-1'), bytes(ct, 'latin-1')) for iv, ct in data]



if __name__ == "__main__":
    seed = b'test'
    messages = ['test', 'tatatat']

    client_instance = Client(seed, 0)
    cloud_instance = Cloud(client_instance.g__, messages)

    w__ = client_instance.get_w(cloud_instance.rand__)
    save_to_json('data/ot/w.json', w__)

    l_w = load_from_json('data/ot/w.json')
    deserialized_w__ = deserialize_w(l_w)
    keys = cloud_instance.get_keys(deserialized_w__)
    save_to_json('data/ot/keys.json', keys)

    l_keys = load_from_json('data/ot/keys.json')
    deserialized_keys = deserialize_keys(l_keys)
    ciphertexts = cloud_instance.encode(deserialized_keys)
    save_to_json('data/ot/ciphertexts.json', ciphertexts)

    l_ciphertexts = load_from_json('data/ot/ciphertexts.json')
    deserialized_ciphertexts = deserialize_ciphertexts(l_ciphertexts)
    plain = client_instance.decode(ciphertexts)
    print(plain)