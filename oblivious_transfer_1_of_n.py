import json
import sys
from typing import Any, Union

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
    def __init__(self, seed: bytes, index: int) -> None:
        self.g__ = G1.hashAndMapTo(seed)
        self.alpha = Fr()
        self.index = index

    def get_w(self, rand__: list[G1]) -> G1:
        self.alpha = Fr.rnd()
        return rand__[self.index] * self.alpha

    def decode(self, ciphertexts: list[bytes]) -> bytes:
        key = (self.g__ * self.alpha).getStr()
        return byte_xor(key, ciphertexts[self.index])


class Cloud:
    def __init__(self, seed: bytes, messages: list[bytes]) -> None:
        self.g__ = G1.hashAndMapTo(seed)
        self.messages = messages
        self.rand_ = [Fr.rnd() for _ in messages]
        self.rand__ = [self.g__ * rand_ for rand_ in self.rand_]

    def get_keys(self, w__: G1) -> list[bytes]:
        neutral_element = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
        return [((w__ * (neutral_element / rand_)).getStr()) for rand_ in self.rand_]

    def encode(self, keys: list[bytes]) -> list[bytes]:
        return [byte_xor(key, message) for key, message in zip(keys, self.messages)]


def deserialize_rand(data):
    return [deserialize_to_g1(d) for d in data]


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
        b"eps1.2_d3bug.mkv",
        b"eps1.3_da3m0ns.mp4",
        b"eps1.4_3xpl0its.wmv",
        b"eps1.5_br4ve-trave1er.asf",
        b"eps1.6_v1ew-s0urce.flv",
        b"eps1.7_wh1ter0se.m4v",
        b"eps1.8_m1rr0r1ng.qt",
        b"eps1.9_zer0-day.avi"
    ]

    client_instance = Client(seed, 2)
    cloud_instance = Cloud(seed, messages)

    save_to_json('data/ot/rand.json', cloud_instance.rand__)

    l_rand = load_from_json('data/ot/rand.json')
    deserialized_rand__ = deserialize_rand(l_rand)
    w__ = client_instance.get_w(deserialized_rand__)
    save_to_json('data/ot/w.json', w__)

    l_w = load_from_json('data/ot/w.json')
    deserialized_w__ = deserialize_to_g1(l_w)
    keys = cloud_instance.get_keys(deserialized_w__)
    save_to_json('data/ot/keys.json', keys)

    l_keys = load_from_json('data/ot/keys.json')
    deserialized_keys = deserialize_to_bytes(l_keys)
    ciphertexts = cloud_instance.encode(deserialized_keys)
    save_to_json('data/ot/ciphertexts.json', ciphertexts)

    l_ciphertexts = load_from_json('data/ot/ciphertexts.json')
    deserialized_ciphertexts = deserialize_to_bytes(l_ciphertexts)
    plain = client_instance.decode(deserialized_ciphertexts)
    print(plain)
