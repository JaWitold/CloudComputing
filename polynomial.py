import json
import sys

from typing import List, Tuple, Any, Union
from functools import reduce
from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


def get_file_id(file_path: str) -> str:
    seed__ = b""
    with open(file_path, 'rb') as file:
        seed__ += file.readline()
    return G1().hashAndMapTo(seed__).getStr()


def li_exp(x_: Fr, A: List[Tuple[Fr, Fr]]) -> G1:
    neutral_element_multiplier__ = G1().hashAndMapTo(b'1') - G1().hashAndMapTo(b'1')
    neutral_element_sum_ = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
    return reduce(lambda res_1, q: res_1 + (
            q[1] * reduce(lambda res_2, p: res_2 * (x_ - p[0]) / (q[0] - p[0]) if q[0] != p[0] else res_2, A,
                          neutral_element_sum_)), A, neutral_element_multiplier__)


def get_unique_random_fr(existing_: List[Fr]) -> Fr:
    while True:
        rand_value_ = Fr.rnd()
        if all(m_i_ != rand_value_ for m_i_ in existing_):
            return rand_value_


def get_polynomial_value(coefficients_: List[Fr], x_value_: Fr) -> Fr:
    value_ = Fr()
    for coefficient_ in reversed(coefficients_):
        value_ = value_ * x_value_ + coefficient_
    return value_


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
    def __init__(self, seed: bytes, file_path: str) -> None:
        self.key_file__ = None
        self.m_ = None
        self.secret_key_ = None
        self.raw_m_ = None
        self.g__ = None
        self.file_path = file_path
        self.setup(seed)

    def check_proof(self, proof_file__: G1) -> bool:
        return self.key_file__ == proof_file__

    def split_file_into_chunks(self, chunk_size: int = 8) -> None:
        self.raw_m_ = []
        with open(self.file_path, 'rb') as file:
            while chunk := file.read(chunk_size):
                self.raw_m_.append(chunk)
        self.convert_chunks_to_fr()

    def convert_chunks_to_fr(self):
        self.m_ = []
        for i, chunk in enumerate(self.raw_m_):
            value_ = Fr()
            value_.setInt(int.from_bytes(chunk, 'little') + i)
            self.m_.append(value_)

    def setup(self, seed: bytes) -> None:
        self.g__ = G1().hashAndMapTo(seed)
        self.secret_key_ = Fr.rnd()

    def get_polynomial(self) -> List[Fr]:
        file_id__ = get_file_id(self.file_path)
        return [Fr.setHashOf(bytes(self.secret_key_) + file_id__ + bytes(i)) for i in range(len(self.m_) + 1)]

    def tag_blocks(self) -> List[Tuple[bytes, Fr]]:
        coefficients_ = self.get_polynomial()
        return [(raw, get_polynomial_value(coefficients_, m_value_)) for raw, m_value_ in
                zip(self.raw_m_, self.m_)]

    def generate_challenge(self) -> Tuple[G1, Fr, G1]:
        coefficients_ = self.get_polynomial()
        random_value_ = Fr.rnd()
        unique_random_value_ = get_unique_random_fr(self.m_)
        self.key_file__ = self.g__ * (random_value_ * get_polynomial_value(coefficients_, unique_random_value_))
        return self.g__ * random_value_, unique_random_value_, self.g__ * (
                random_value_ * get_polynomial_value(coefficients_, Fr()))


class Cloud:
    def __init__(self, g__: G1) -> None:
        self.tagged_file = None
        self.g__ = g__

    @staticmethod
    def deserialize_tagged_file(json_data: List[List[Union[str, bytes]]]) -> List[Tuple[bytes, Fr]]:
        deserialized_data = []
        for item in json_data:
            if len(item) == 2:
                raw_data = bytes(item[0], 'latin-1')
                fr_value_ = Fr()
                fr_value_.setStr(bytes(item[1], 'latin-1'))
                deserialized_data.append((raw_data, fr_value_))
        return deserialized_data

    def convert_chunks_to_fr(self) -> None:
        for i, (chunk, tag_) in enumerate(self.tagged_file):
            value_ = Fr()
            value_.setInt(int.from_bytes(chunk, 'little') + i)
            self.tagged_file[i] = (value_, tag_)

    def upload_file(self, tagged_file: List[Tuple[bytes, Fr]]) -> None:
        self.tagged_file = tagged_file
        self.convert_chunks_to_fr()

    def generate_proof(self, challenge: Tuple[G1, Fr, G1]) -> G1:
        gr__, x_value_, grlf_0__ = challenge
        ksi_ = [(m_value_, gr__ * tag_) for m_value_, tag_ in self.tagged_file]
        ksi_.append((Fr(), grlf_0__))
        return li_exp(x_value_, ksi_)

    @staticmethod
    def deserialize_challenge(json_data: List[str]) -> Tuple[G1, Fr, G1]:
        g_value__ = G1()
        x_value_ = Fr()
        g_coefficient__ = G1()

        if len(json_data) == 3:
            g_value__.setStr(bytes(json_data[0], 'latin-1'))
            x_value_.setStr(bytes(json_data[1], 'latin-1'))
            g_coefficient__.setStr(bytes(json_data[2], 'latin-1'))
        return g_value__, x_value_, g_coefficient__


if __name__ == "__main__":
    file_path = './data/randomfile_1K'
    seed_value = b'test'

    client_instance = Client(seed_value, file_path)
    cloud_instance = Cloud(client_instance.g__)
    client_instance.split_file_into_chunks()
    tagged_file = client_instance.tag_blocks()
    save_to_json('data/tagged_file.json', tagged_file)

    loaded_data = load_from_json('data/tagged_file.json')
    cloud_tagged_file = cloud_instance.deserialize_tagged_file(loaded_data)
    cloud_instance.upload_file(cloud_tagged_file)

    challenge = client_instance.generate_challenge()
    save_to_json('data/challenge.json', challenge)

    loaded_challenge = load_from_json('data/challenge.json')
    cloud_challenge = cloud_instance.deserialize_challenge(loaded_challenge)
    proof_file__ = cloud_instance.generate_proof(cloud_challenge)
    save_to_json('data/proof_file.json', proof_file__)

    loaded_proof_file__ = load_from_json('data/proof_file.json')
    if isinstance(loaded_proof_file__, str):
        proof_file__ = G1()
        proof_file__.setStr(bytes(loaded_proof_file__, 'latin-1'))
        if client_instance.check_proof(proof_file__):
            print("Proof verified!")
        else:
            print("Proof failed!")
