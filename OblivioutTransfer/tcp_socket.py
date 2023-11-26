import socket
import pickle
import struct
from typing import Any


def send(tcp_socket: socket, message: Any):
    encoded_msg = pickle.dumps(message)
    packed_msg = struct.pack('>I', len(encoded_msg)) + encoded_msg

    tcp_socket.sendall(packed_msg)


def receive_all(tcp_socket: socket, nr_bytes: int):
    received_bytes = bytearray()
    while len(received_bytes) < nr_bytes:
        packet = tcp_socket.recv(nr_bytes - len(received_bytes))
        if not packet:
            return None

        received_bytes.extend(packet)

    return received_bytes


def receive(tcp_socket: socket):
    packed_nr_bytes_to_receive = receive_all(tcp_socket, 4)
    if not packed_nr_bytes_to_receive:
        return None

    nr_bytes_to_receive = struct.unpack('>I', packed_nr_bytes_to_receive)[0]

    packed_message = receive_all(tcp_socket, nr_bytes_to_receive)
    message = pickle.loads(packed_message)

    return message
