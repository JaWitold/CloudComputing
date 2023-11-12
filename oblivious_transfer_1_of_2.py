import json
import sys
from typing import Any, Union
import hashlib

from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])


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
    def __init__(self, seed: bytes, c: int) -> None:
        self.key: bytes = b''
        self.g__ = G1.hashAndMapTo(seed)
        self.b_ = Fr.rnd()
        self.c = c % 2

    def get_b__(self, a__: G1) -> G1:
        b__ = self.g__ * self.b_
        self.key = hashlib.sha256((a__ * self.b_).getStr()).digest()
        return b__ if self.c == 0 else a__ + b__

    def decode(self, ciphertexts: list[bytes]) -> bytes:
        return byte_xor(self.key, ciphertexts[self.c])


class Cloud:
    def __init__(self, seed: bytes, messages: list[bytes]) -> None:
        self.g__ = G1.hashAndMapTo(seed)
        self.a_ = Fr.rnd()
        self.messages = messages

    def get_a__(self) -> G1:
        return self.g__ * self.a_

    def get_keys(self, b__: G1) -> list[bytes]:
        return [hashlib.sha256((b__ * self.a_).getStr()).digest(),
                hashlib.sha256(((b__ - self.get_a__()) * self.a_).getStr()).digest()]

    def encode(self, keys: list[bytes]) -> list[bytes]:
        return [byte_xor(key, message) for key, message in zip(keys, self.messages)]


def deserialize_to_g1(data: str):
    g = G1()
    g.setStr(bytes(data, 'latin-1'))
    return g


def deserialize_to_bytes(data):
    return [bytes(key, 'latin-1') for key in data]


if __name__ == "__main__":
    seed = b'test'
    messages = [
        b"eps1.0_hellofriend.mov",
        b"eps1.1_ones-and-zer0es.mpeg",
    ]

    client_instance = Client(seed, 1)
    cloud_instance = Cloud(seed, messages)

    save_to_json('data/otp/a__.json', cloud_instance.get_a__())

    l_a__ = load_from_json('data/otp/a__.json')
    b__ = client_instance.get_b__(deserialize_to_g1(l_a__))
    save_to_json('data/otp/b__.json', b__)

    l_b__ = load_from_json('data/otp/b__.json')
    keys = cloud_instance.get_keys(deserialize_to_g1(l_b__))
    ciphertexts = cloud_instance.encode(keys)
    save_to_json('data/otp/ciphertexts.json', ciphertexts)

    l_ciphertexts = load_from_json('data/otp/ciphertexts.json')
    deserialized_ciphertexts = deserialize_to_bytes(l_ciphertexts)
    plain = client_instance.decode(deserialized_ciphertexts)
    print(plain)
