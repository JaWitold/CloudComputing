import json
import sys

from functools import reduce
from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


def get_file_id(file_path):
    seed = b""
    with open(file_path, 'rb') as file:
        seed += file.readline()
    return G1().hashAndMapTo(seed).getStr()


def get_rand_from_fr_based_on_seed(seed: bytes):
    return Fr.setHashOf(seed)


def LI_exp(x: Fr, A):
    nem = G1().hashAndMapTo(b'1') - G1().hashAndMapTo(b'1')
    nes = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
    return reduce(lambda res_1, q: res_1 + (
            q[1] * reduce(lambda res_2, p: res_2 * (x - p[0]) / (q[0] - p[0]) if q[0] != p[0] else res_2, A, nes)),
                  A, nem)


def get_pairwise_different_random_fr(m):
    while True:
        xc = Fr.rnd()
        cond = True
        for m_i in m:
            if m_i == xc:
                cond = False
                break
        if cond:
            break
    return xc


def get_polynomial_value(lf, xc: Fr):
    value = Fr()
    for ai in reversed(lf):
        value = value * xc + ai
    return value


class Client:
    def __init__(self, seed: bytes, file_path):
        self.Kf = None
        self.m = None
        self.sk_c = None
        self.raw_m = None
        self.g = None
        self.file_path = file_path

        self.setup(seed)

    def check_proof(self, Pf):
        return self.Kf == Pf

    def split_file_into_bytes(self, z=8):
        with open(self.file_path, 'rb') as file:
            file_content = file.read()
        chunk_size = len(file_content) // z
        self.raw_m = []

        for i in range(z):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            byte_chunk = file_content[start:end]
            self.raw_m.append(byte_chunk)

        if end < len(file_content):
            self.raw_m[-1] += file_content[end:]
        self.chunks_to_fr()

    # def split_file_into_bytes(self, z=8):
    #     self.raw_m = []
    #     with open(self.file_path, 'rb') as file:
    #         for _ in file:
    #             self.raw_m.append(file.read(z))
    #     print(self.raw_m)
    #     self.chunks_to_fr()

    def chunks_to_fr(self):
        self.m = []
        for i, f_i in enumerate(self.raw_m):
            p = Fr()
            p.setInt(int.from_bytes(f_i, 'little') + i)
            self.m.append(p)

    def setup(self, seed: bytes):
        self.g = G1().hashAndMapTo(seed)
        # self.sk_c = Fr.setHashOf(b'1')
        self.sk_c = Fr.rnd()

    def poly(self):
        file_id = get_file_id(self.file_path)
        return [get_rand_from_fr_based_on_seed(bytes(self.sk_c) + file_id + bytes(i)) for i in range(len(self.m) + 1)]

    def tag_block(self):
        lf = self.poly()
        return [(raw, get_polynomial_value(lf, m_i)) for raw, m_i in zip(self.raw_m, self.m)]

    def gen_challenge(self):
        lf = self.poly()
        r = Fr.rnd()
        xc = get_pairwise_different_random_fr(self.m)
        self.Kf = self.g * (r * get_polynomial_value(lf, xc))
        return self.g * r, xc, self.g * (r * get_polynomial_value(lf, Fr()))


class Cloud:
    def __init__(self, g: G1):
        self.Tf = None
        self.g = g

    def deserialize_Tf(self, json_data):
        deserialized_data = []
        for item in json_data:
            if len(item) == 2:
                first_item = bytes(item[0], 'latin-1')
                second_item = Fr()
                second_item.setStr(bytes(item[1], 'latin-1'))
                deserialized_data.append((first_item, second_item))
        return deserialized_data
    def chunks_to_fr(self):
        for i, f_i in enumerate(self.Tf):
            # print(f_i)
            # exit()
            p = Fr()
            p.setInt(int.from_bytes(f_i[0], 'little') + i)
            t = (p, f_i[1])
            self.Tf[i] = t
    def upload_file(self, Tf):
        self.Tf = Tf
        self.chunks_to_fr()

    def gen_proof(self, H):
        gr, xc, grLF_0 = H
        ksi = [(mi, gr * ti) for mi, ti in self.Tf]
        ksi.append((Fr(), grLF_0))
        return LI_exp(xc, ksi)

    def deserialize_H(self, json_data):
        deserialized_data = []
        if len(json_data) == 3:
            first = G1()
            first.setStr(bytes(json_data[0], 'latin-1'))

            second = Fr()
            second.setStr(bytes(json_data[1], 'latin-1'))

            third = G1()
            third.setStr(bytes(json_data[2], 'latin-1'))
        return (first, second, third)


def custom_encoder(obj):
    if hasattr(obj, 'serialize'):
        return obj.getStr()
    elif isinstance(obj, bytes):
        return obj.decode('latin-1')
    raise TypeError("Object of unsupported type")


def save_to_json(file_path, value):
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(value, default=custom_encoder))


def load_from_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data


if __name__ == "__main__":
    file_path = './schnorr.py'
    seed = b'test'

    client = Client(seed, file_path)
    cloud = Cloud(seed)
    client.split_file_into_bytes()
    Tf = client.tag_block()
    save_to_json('data/Tf.json', Tf)

    json_data = load_from_json('data/Tf.json')
    Tf_cloud = cloud.deserialize_Tf(json_data)
    cloud.upload_file(Tf_cloud)

    H = client.gen_challenge()
    save_to_json('data/H.json', H)

    json_data = load_from_json('data/H.json')
    H_cloud = cloud.deserialize_H(json_data)
    Pf = cloud.gen_proof(H_cloud)
    save_to_json('data/Pf.json', Pf)

    Pf_cloud = G1()
    Pf_cloud.setStr(bytes(load_from_json('data/Pf.json'), 'latin-1'))

    print(client.check_proof(Pf_cloud))
