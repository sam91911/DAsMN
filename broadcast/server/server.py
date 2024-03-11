from authorize import *
from connect import *
from filesys import *
from base64 import b64encode, b64decode
import os
import json
import socket

class Server:
    def __init__(self, host, port, passward, base_dir, key_dir = "key", author_dir = "author", trust_dir = "trust", file_dir = "files", name_dir = "name", use_saved_salt=True):
        # Initialize the components
        self.network = NetworkConnection(host, port, self.serve_function, [self, ])
        self.filesys = TimeSortedFileSystem(os.path.join(base_dir, file_dir))
        self.keysys = KeyFileSystem(os.path.join(base_dir, key_dir), passward, is_password=True, use_saved_salt=True)
        self.authorsys = AuthorizationFilesHandler(os.path.join(base_dir, author_dir))
        self.trustsys = TrustedServerManager(os.path.join(base_dir, trust_dir))
        self.namesys = NameFileSystem(os.path.join(base_dir, name_dir))

    def start(self):
        # Start the network connection
        self.network.start()

    def shutdown(self):
        # Shutdown the network connection
        self.network.close()

    def login_check(self, nonce_send, rt, slient_socket):
        try:
            server_name = rt["server_name"]
            nonce_recv = bytes.fromhex(rt["nonce"])
            hash_recv = bytes.fromhex(rt["hmac"])
            iv = rt["iv"]
            data = rt["data"]
        except KeyError:
            return None
        if (len(nonce_recv) != 16) or (len(hash_recv) != 32):
            return None
        if not self.authorsys.check_server(server_name):
            return None
        server_key = self.keysys.load_key(server_name)
        if not AuthorizationSystem.hmac_check(nonce_send, hash_recv, nonce_recv, server_key):
            return None
        symsys = SymmetricEncryptionSystem()
        symsys.set_key(server_key, iv)
        try:
            data = json.loads(symsys.decrypt_data(data))
        except:
            return None
        try:
            user = data["user"]
            sign = b64decode(data["sign"])
        except:
            return None
        user_name = self.namesys.get_user_name(user, server_name)
        if not self.authorsys.check_user_right(server_name, "user", user):
            return None
        if not AuthorizationSystem.authorize_user(nonce_send, sign, nonce_recv, b64decode(user.encode())):
            return None
        return user, user_name

    def login_reply(self, nonce_send, nonce_recv, server_name):
        return None

    @staticmethod
    def serve_function(server, exit_signal, client_socket):
        buffer_size = 4096
        nonce_send = AuthorizationSystem.generate_nonce()
        client_socket.sendall(nonce_send)
        while not exit_signal.is_set():
            try:
                client_socket.settimeout(1)
                data_recv = client_socket.recv(buffer_size).decode()
            except socket.timeout:
                if self.shutdown_signal.is_set():
                    client_socket.close()
                    return
            else:
                break
        try:
            rt = json.loads(data_recv)
        except json.decoder.JSONDecodeError:
            client_socket.sendall("It's a DAsMN server".encode())
            return
        if not isinstance(rt, dict):
            client_socket.sendall("It's a DAsMN server".encode())
            return
        user_key, user_name = server.login_check(nonce_send, rt, client_socket)
        if user is None:
            client_socket.sendall("Wrong server".encode())
            return
        server.filesys.store_file(rt["server_name"], user_name, user_key, data_recv)
        client_socket.sendall(server.login_reply(nonce_send, bytes.fromhex(rt["nonce"]), rt["server_name"]))
        return
