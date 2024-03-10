from authorize import *
from connect import *
from filesys import *
import os
import json

class Server:
    def __init__(self, host, port, passward, base_dir, key_dir = "key", author_dir = "author", trust_dir = "trust", file_dir = "files", use_saved_salt=True):
        # Initialize the components
        self.network = NetworkConnection(host, port, self.serve_function, [self, ])
        self.filesys = TimeSortedFileSystem(os.path.join(base_dir, file_dir))
        self.keysys = KeyFileSystem(os.path.join(base_dir, key_dir), passward, is_password=True, use_saved_salt=True)
        self.authorsys = AuthorizationFilesHandler(os.path.join(base_dir, author_dir))
        self.trustsys = TrustedServerManager(os.path.join(base_dir, trust_dir))

    def start(self):
        # Start the network connection
        self.network.start()

    def shutdown(self):
        # Shutdown the network connection
        self.network.close()

    def login_check(self, nonce_send, rt, slient_socket):
        try:
            server_name = rt["server_name"]
            nonce_recv = rt["nonce"]
            hash_recv = rt["hmac"]
            server_data = rt["data"]
        except KeyError:
            client_socket.sendall("It's a DAsMN server\r\n".encode())
            return False
        if (len(nonce_recv) != 16) or (len(hash_recv) != 32):
            client_socket.sendall("It's a DAsMN server\r\n".encode())
            return False
        if not self.authorsys.check_server(server_name):
            client_socket.sendall("Wrong server\r\n".encode())
            return False
        server_key = self.keysys.load_key(server_name)
        try:
            nonce_recv = bytes.fromhex(nonce_recv)
            hash_recv = bytes.fromhex(hash_recv)
        except ValueError:
            client_socket.sendall("It's a DAsMN server\r\n".encode())
            return False
        if not AuthorizationSystem.hmac_check(nonce_send, hash_recv, nonce_recv, server_key):
            client_socket.sendall("Wrong server\r\n".encode())
            return False
        symsys = SymmetricEncryptionSystem()
        symsys.set_key(server_key, nonce_recv)
        try:
            server_data = json.loads(symsys.decrypt_data(server_data))
            user = server_data["user"]
            sign = server_data["sign"]

        if not self.authorsys.check_user_right(server_name, "user", user):
            client_socket.sendall("Wrong server\r\n".encode())
            return False




    @staticmethod
    def serve_function(server, exit_signal, client_socket):
        buffer_size = 4096
        nonce_send = AuthorizationSystem.generate_nonce()
        client_socket.sendall(nonce_send)
        while not self.shutdown_signal.is_set():
            try:
                client.socket.settimeout(1)
                rt = json.loads(client_socket.recv(buffer_size).decode())
            except socket.timeout:
                if self.shutdown_signal.is_set():
                    client_socket.close()
                    return
            except json.decoder.JSONDecodeError:
                client_socket.sendall("It's a DAsMN server\r\n".encode())
                return
            else:
                if not isinstance(rt, dict):
                    client_socket.sendall("It's a DAsMN server\r\n".encode())
                    return
                else:
                    break
        if not server.login_check(nonce_send, rt, client_socket):
            return
        return
