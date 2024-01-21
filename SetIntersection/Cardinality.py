import random
import socket
import sys

from mcl import G1, Fr

from tcp_socket import send, receive


class Server:
    def __init__(self, elements: list[bytes]):
        self.__server_hashes = [G1.hashAndMapTo(element) for element in elements]
        random.shuffle(self.__server_hashes)

    def __process_data_from_client(self, client_hashes: list[G1]):
        r_s = Fr.rnd()

        processed_client_hashes = [client_hash * r_s for client_hash in client_hashes]
        random.shuffle(client_hashes)

        return (processed_client_hashes, [G1.hashAndMapTo((server_hash * r_s).getStr()) for server_hash in
                                          self.__server_hashes])

    @staticmethod
    def execute_protocol(data: list, ip: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.bind((ip, port))
            tcp_socket.listen()
            client_socket, _ = tcp_socket.accept()
            client_hashes = receive(client_socket)
            server = Server(data)
            client_hashes_processed_by_server, server_hashes = server.__process_data_from_client(client_hashes)
            send(client_socket, (client_hashes_processed_by_server, server_hashes))


class Client:
    def __init__(self):
        self.R_c = Fr.rnd()

    def __calculate_set_intersection(self, client_hashes_processed_by_server: list[G1], server_hashes: list[G1]):
        one = Fr()
        one.setInt(1)
        return {(G1.hashAndMapTo((client_hash * (one / self.R_c)).getStr())).getStr() for client_hash in
                client_hashes_processed_by_server} & {server_hash.getStr() for server_hash in server_hashes}

    @staticmethod
    def execute_protocol(data: list, ip: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            client = Client()
            tcp_socket.connect((ip, port))
            send(tcp_socket, [G1.hashAndMapTo(element) * client.R_c for element in data])
            client_hashes_processed_by_server, server_hashes = receive(tcp_socket)
            return len(client.__calculate_set_intersection(client_hashes_processed_by_server, server_hashes))


if __name__ == "__main__":
    ip = sys.argv[2]
    port = int(sys.argv[3])

    if sys.argv[1] == "server":
        server_data = [b'2', b'3', b'4', b'5']

        Server.execute_protocol(server_data, ip, port)
    elif sys.argv[1] == "client":
        client_data = [b'1', b'2', b'3']
        csi = Client.execute_protocol(client_data, ip, port)
        print(f"Cardinality of intersection of sets is {csi}")

    else:
        raise ValueError("Invalid argument.")
