import hashlib
import math
import socket
import sys
from typing import List

from mcl import Fr, G1

from oblivious_transfer_1_of_2 import Client as OTClient, Cloud as OTServer
from tcp_socket import send, receive
from util import byte_xor

sys.path.insert(1, '/home/jawitold/mcl')


class Client:
    """
    Client class for performing secure computation tasks.
    """

    def __init__(self):
        """
        Initializes the Client instance.
        """
        pass

    @staticmethod
    def execute(seed: bytes, ip: str, port: int, inputs: List[int]):
        """
        Executes the client's part of the secure computation protocol.

        Args:
        seed (bytes): Seed used for cryptographic operations.
        ip (str): IP address of the server.
        port (int): Port number for the connection.
        inputs (List[int]): List of binary inputs for the computation.
        """
        # Create a TCP socket and connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((ip, port))
            # Receive encoded data from the server
            number_of_ot = receive(client_socket)
            assert number_of_ot == len(inputs), "number of inputs differs from required number of oblivious transfers"

            # Receive encoded data from the server
            encoded = receive(client_socket)
            client_socket.close()

        # Perform oblivious transfer for each bit in the inputs
        outputs = [OTClient.execute(seed, bit, ip, port) for bit in inputs]
        # Convert binary inputs to an integer index
        index = int("".join(str(e) for e in inputs), 2)
        # Decode the received message using the outputs from oblivious transfer
        decoded = encoded[index]
        for key in outputs:
            decoded = byte_xor(decoded, key)
        print(int(decoded))


class Server:
    """
    Server class for performing secure computation tasks.
    """

    def __init__(self, seed: bytes, secret_circuit: list):
        """
        Initializes the Server instance.

        Args:
        seed (bytes): Seed used for cryptographic operations.
        secret_circuit (list): List representing the secret circuit for computation.
        """
        assert self.is_power_of_two(len(secret_circuit)), "Length of secret_circuit must be a power of 2."

        # Generate an element in G1 using the seed
        self.g__ = G1.hashAndMapTo(seed)
        self.circuit = secret_circuit
        # Determine the number of bits required to represent all possible inputs
        self.number_of_possible_inputs = math.ceil(math.log2(len(self.circuit)))
        self.keys = []

    def gen_keys(self):
        """
        Generates cryptographic keys for each input bit.
        """
        # Generate a pair of keys for each bit in the input
        self.keys = [(self.key_gen(), self.key_gen()) for _ in range(self.number_of_possible_inputs)]

    def key_gen(self):
        """
        Generates a single cryptographic key.

        Returns:
        bytes: A generated cryptographic key.
        """
        # Generate a random element in Fr, multiply with g__, hash it and return
        return hashlib.sha256((self.g__ * Fr.rnd()).getStr()).digest()

    @staticmethod
    def execute(seed: bytes, ip: str, port: int, secret_circuit: list):
        """
        Executes the server's part of the secure computation protocol.

        Args:
        seed (bytes): Seed used for cryptographic operations.
        ip (str): IP address for the server.
        port (int): Port number for the server.
        secret_circuit (list): List representing the secret circuit for computation.
        """
        # Initialize and prepare the server
        srv = Server(seed, secret_circuit)
        srv.gen_keys()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((ip, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()
            # Send the encoded data to the client
            send(client_socket, srv.number_of_possible_inputs)

            encoded = []
            # Encode each value in the circuit
            for index, value in enumerate(srv.circuit):
                # Convert index to binary and pad with zeros
                bin_index = [int(a) for a in list(bin(index)[2:].zfill(srv.number_of_possible_inputs))]
                ciphertext = bytes(str(value).zfill(32), 'utf-8')
                # XOR the ciphertext with the appropriate keys
                for key_index in range(srv.number_of_possible_inputs):
                    ciphertext = byte_xor(ciphertext, srv.keys[key_index][bin_index[key_index]])
                encoded.append(ciphertext)

            # Send the encoded data to the client
            send(client_socket, encoded)
            client_socket.close()

        # Execute oblivious transfer for each pair of keys
        for keys in srv.keys:
            OTServer.execute(seed, list(keys), ip, port)

    @staticmethod
    def is_power_of_two(n: int) -> bool:
        """
        Checks if a number is a power of two.

        Args:
        n (int): The number to check.

        Returns:
        bool: True if n is a power of two, False otherwise.
        """
        return n != 0 and (n & (n - 1)) == 0


# Main execution block
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("Invalid number of args.")

    ip = sys.argv[2]
    port = int(sys.argv[3])

    seed = b"test"
    # Define the secret circuit
    if sys.argv[1] == "server":
        Server.execute(seed, ip, port, [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1])
    elif sys.argv[1] == "client":
        Client.execute(seed, ip, port, [0, 1, 0, 0])
    else:
        raise ValueError("Invalid argument.")
