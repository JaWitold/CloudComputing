import sys
from tcp_socket import *
import socket
from util import byte_xor

from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


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

    @staticmethod
    def execute(seed: bytes, index: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((ip, port))
            client = Client(seed, index)
            rs = receive(tcp_socket)
            w = client.get_w(rs)
            send(tcp_socket, w)
            encoded_response = receive(tcp_socket)
            return pickle.loads(client.decode(encoded_response))


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

    @staticmethod
    def execute(seed: bytes, messages: list):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((ip, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()

            serialized_messages = [pickle.dumps(message) for message in messages]
            server = Cloud(seed, serialized_messages)
            send(client_socket, server.rand__)
            w = receive(client_socket)
            keys = server.get_keys(w)
            ciphertexts = server.encode(keys)
            send(client_socket, ciphertexts)


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

    if len(sys.argv) < 4:
        raise ValueError("Invalid number of args.")

    ip = sys.argv[2]
    port = int(sys.argv[3])
    index = int(sys.argv[4])

    if sys.argv[1] == "server":
        Cloud.execute(seed, messages)
    elif sys.argv[1] == "client":

        print(Client.execute(seed, index))
    else:
        raise ValueError("Invalid argument.")
