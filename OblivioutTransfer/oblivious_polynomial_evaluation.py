import pickle
from typing import List, Tuple

import numpy as np
import sys
import socket
from oblivious_transfer_1_of_n import Client, Cloud
from util import int_to_fr, get_polynomial_value, lagrange_interpolation
from tcp_socket import send, receive

from mcl import Fr, G1

sys.path.insert(1, '/home/jawitold/mcl')


class Receiver:
    def __init__(self, seed: bytes, dp: int, k: int, m: int):
        self.random_arguments = None
        self.T = None
        self.alpha = None
        self.seed = seed
        self.dp = dp
        self.k = k
        self.m = m
        self.n = self.k * self.dp + 1
        self.N = self.n * self.m

    def get_request_for_sender(self, alpha: int) -> List[Tuple[Fr, Fr]]:
        self.alpha = alpha

        random_polynomial = [Fr.rnd() for _ in range(self.k)]
        random_polynomial[-1].setInt(self.alpha)

        self.T = np.random.choice(range(self.N), self.n, replace=False)
        self.random_arguments = [Fr.rnd() for _ in range(self.N)]

        return [((random_argument, get_polynomial_value(random_polynomial, random_argument)) if i in self.T else (
            random_argument, Fr.rnd())) for i, random_argument in enumerate(self.random_arguments)]

    def ope(self, tcp_socket: socket, alpha: int):
        request_for_sender = self.get_request_for_sender(alpha)
        send(tcp_socket, request_for_sender)
        polynomial_samples = []

        for index in self.T:
            polynomial_samples.append(self.execute(self.seed, index, tcp_socket))

        return lagrange_interpolation(Fr(), polynomial_samples)

    @staticmethod
    def execute(seed: bytes, index: int, tcp_socket: socket):
        client = Client(seed, index)
        rs = receive(tcp_socket)
        w = client.get_w(rs)
        send(tcp_socket, w)
        encoded_response = receive(tcp_socket)
        return pickle.loads(client.decode(encoded_response))


class Sender:
    def __init__(self, seed: bytes, k: int, P: list[Fr]):
        self.seed = seed
        self.dp = len(P) - 1
        self.k = k

        self.Px = [Fr.rnd() for _ in range(self.dp * self.k)]
        self.Px[-1].setInt(0)

        self.P = P

    def get_data_for_receiver(self, arguments: list[list[Fr]]):
        data_for_receiver = []

        for x, y in arguments:
            sample = (x, (get_polynomial_value(self.Px, x) + get_polynomial_value(self.P, y)))
            data_for_receiver.append(sample)

        return data_for_receiver

    def ope(self, tcp_socket: socket):
        request_for_sender = receive(tcp_socket)
        polynomial_samples = self.get_data_for_receiver(request_for_sender)

        for _ in range(n):
            self.execute(self.seed, polynomial_samples, tcp_socket)

    @staticmethod
    def execute(seed: bytes, messages: list, client_socket: socket):
        serialized_messages = [pickle.dumps(message) for message in messages]
        server = Cloud(seed, serialized_messages)
        send(client_socket, server.rand__)
        w = receive(client_socket)
        keys = server.get_keys(w)
        ciphertexts = server.encode(keys)
        send(client_socket, ciphertexts)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("Invalid number of args.")

    IP = sys.argv[2]
    port = int(sys.argv[3])

    seed = b"test"
    server_polynomial = [int_to_fr(2), int_to_fr(0), int_to_fr(0)]

    d_p = len(server_polynomial) - 1
    k = 3
    n = d_p * k + 1
    m = 10
    alpha = 10

    if sys.argv[1] == "server":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((IP, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()
            server = Sender(seed, k, server_polynomial)
            server.ope(client_socket)
    elif sys.argv[1] == "client":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((IP, port))

            client = Receiver(seed, d_p, k, m)
            print(client.ope(client_socket, alpha))
    else:
        raise ValueError("Invalid argument.")
