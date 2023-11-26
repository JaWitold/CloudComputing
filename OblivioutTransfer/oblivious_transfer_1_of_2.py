import sys
from typing import List
import hashlib
from util import byte_xor
import socket

from tcp_socket import send, receive
from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


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

    @staticmethod
    def execute(seed: bytes, client_index: int, ip: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((ip, port))

            client = Client(seed, client_index)

            a__ = receive(client_socket)

            b__ = client.get_b__(a__)
            send(client_socket, b__)
            ciphertexts = receive(client_socket)

            decryption = client.decode(ciphertexts)
            print(f"Client: message: \"{decryption}\".")


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

    @staticmethod
    def execute(seed: bytes, messages: List[bytes], ip: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((ip, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()

            server = Cloud(seed, messages)

            a__ = server.get_a__()
            send(client_socket, a__)

            b__ = receive(client_socket)
            keys = server.get_keys(b__)

            ciphertexts = server.encode(keys)
            send(client_socket, ciphertexts)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError("Invalid number of args.")

    IP = sys.argv[2]
    port = int(sys.argv[3])
    index = int(sys.argv[4]) % 2

    seed = b'test'
    messages = [
        b"eps1.0_hellofriend.mov",
        b"eps1.1_ones-and-zer0es.mpeg",
    ]

    if sys.argv[1] == "server":
        Cloud.execute(seed, messages, IP, port)
    elif sys.argv[1] == "client":
        Client.execute(seed, index, IP, port)
    else:
        raise ValueError("Invalid argument.")
