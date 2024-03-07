from authorize import *
from connect import *
from filesys import *
import os

class Server:
    def __init__(self, host, port, passward, base_dir, key_dir = "key", author_dir = "author", trust_dir = "trust", file_dir = "files", use_saved_salt=True):
        # Initialize the components
        self.network = NetworkConnection(host, port, self.serve_function, [self])
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

    @staticmethod
    def serve_function(server, client_socket):
        client_socket.sendall("Hello".encode())
        return
