import socket
import threading

class NetworkConnection:
    def __init__(self, host, port, server_function = None, server_argument = None):
        self.host = host
        self.port = port
        self.socket = None
        self.is_server = False
        self.server_function = server_function
        self.server_argument = server_argument
        self.clients = []
        self.shutdown_signal = threading.Event()

    def start_server(self, reuse = True):
        if self.server_function is None:
            raise ValueError("server_function need to be set")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if reuse:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.is_server = True

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send(self, data):
        if not self.socket:
            raise ConnectionError("Socket is not connected.")
        self.socket.sendall(data.encode("utf-8"))

    def receive(self, buffer_size=4096):
        if not self.socket:
            raise ConnectionError("Socket is not connected.")
        return self.socket.recv(buffer_size).decode("utf-8")

    def accept_connections(self):
        if not self.is_server:
            raise RuntimeError("Not a server.")
        while not self.shutdown_signal.is_set():
            try:
                # Wait for a connection or until the shutdown signal is set
                self.socket.settimeout(1)  # Set a timeout to periodically check the shutdown signal
                client_socket, _ = self.socket.accept()
                self.clients.append(client_socket)
            except socket.timeout:
                # Check if the shutdown signal is set
                if self.shutdown_signal.is_set():
                    break  # Break out of the loop if the shutdown signal is set
            else:
                # If a connection is accepted, handle it in a new thread
                thread = threading.Thread(target=self.server_function, args=(tuple(self.server_argument+[self.shutdown_signal,client_socket]) if self.server_argument is not None else (self.shutdown_signal, client_socket)))
                thread.start()

    def start(self):
        self.start_server()
        shutdown_thread = threading.Thread(target=self.shutdown_listener)
        shutdown_thread.start()
        self.accept_connections()
        self.shutdown_signal.set()
        shutdown_thread.join()
        if self.socket:
            self.socket.close()
            self.socket = None
        self.is_server = False

    def broadcast(self, message, clients = None):
        clients_to_remove = []
        if clients is None:
            clients = self.clients
        for client_socket in clients:
            try:
                # Attempt to send data
                client_socket.sendall(message.encode())
            except Exception as e:
                # If an exception occurs, the socket is likely closed
                print(f"Error broadcasting to client: {e}")
                clients_to_remove.append(client_socket)

        # Remove closed sockets from the clients list
        for client_socket in clients_to_remove:
            clients.remove(client_socket)

    def shutdown_listener(self):
        while not self.shutdown_signal.is_set():
            if input("Type 'q' to quit: ") == 'q':
                self.close()

    def close(self):
        self.shutdown_signal.set()

    @staticmethod
    def get_ipv4_address():
        ip_addresses = []
        for interface in socket.if_nameindex():
            if_addresses = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
            for if_address in if_addresses:
                ip_addresses.append(if_address[4][0])
        return ip_addresses
