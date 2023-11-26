import json
from functools import reduce
from typing import Any, Union, List, Tuple
from mcl import G1, Fr

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


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


def deserialize_rand(data):
    res = []
    for rand in data:
        rand_ = G1()
        rand_.setStr(bytes(rand, 'latin-1'))
        res.append(rand_)
    return res


def deserialize_g1(data: str):
    g = G1()
    g.setStr(bytes(data, 'latin-1'))
    return g


def deserialize_keys(data):
    return [bytes(key, 'latin-1') for key in data]


def deserialize_ciphertexts(data):
    return [(bytes(iv, 'latin-1'), bytes(ct, 'latin-1')) for iv, ct in data]


def hash_g1_to_bytes(group_element: G1):
    return G1.hashAndMapTo(group_element.getStr()).getStr()
    # return G1.hashAndMapTo(group_element.getStr()).getStr()[:16]


def encrypt_message(message, key: bytes):
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_block = cipher.encrypt(pad(message, AES.block_size))
    return cipher.iv, encrypted_block


def decrypt_message(encrypted_message, key: bytes):
    iv, ciphertext = encrypted_message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, AES.block_size)


def int_to_fr(value: int):
    fr = Fr()
    fr.setInt(value)

    return fr


def get_polynomial_value(coefficients_: List[Fr], x_value_: Fr) -> Fr:
    value_ = Fr()
    for coefficient_ in reversed(coefficients_):
        value_ = value_ * x_value_ + coefficient_
    return value_


def lagrange_interpolation(x_: Fr, A: List[Tuple[Fr, Fr]]) -> Fr:
    neutral_element_multiplier__ = Fr.setHashOf(b'1') - Fr.setHashOf(b'1')
    neutral_element_sum_ = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
    return reduce(lambda res_1, q: res_1 + (
            q[1] * reduce(lambda res_2, p: res_2 * (x_ - p[0]) / (q[0] - p[0]) if q[0] != p[0] else res_2, A,
                          neutral_element_sum_)), A, neutral_element_multiplier__)

