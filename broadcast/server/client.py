from authorize import *
from connect import *
from filesys import *
import os
import json
from base64 import b64encode, b64decode

class Client:
    def __init__(self, host, port, passward, base_dir, key_dir = "key", author_dir = "author", trust_dir = "trust", file_dir = "files", use_saved_salt=True):
        self.network = NetworkConnection(host, port)
        self.filesys = TimeSortedFileSystem(os.path.join(base_dir, file_dir))
        self.keysys = KeyFileSystem(os.path.join(base_dir, key_dir), passward, is_password=True, use_saved_salt=True)
        self.authorsys = AuthorizationFilesHandler(os.path.join(base_dir, author_dir))
        self.trustsys = TrustedServerManager(os.path.join(base_dir, trust_dir))

    def login(self, server, private_key, server_key, public_key):
        replysys = AuthorizationSystem(private_key, server_key)
        encryptsys = SymmetricEncryptionSystem()
        encryptsys.set_key(server_key)
        self.network.connect()
        hs = self.network.socket.recv(1024)
        sign, hmac, nonce_rpl = replysys.reply_authorize(hs)
        sign = b64encode(sign).decode()
        user = b64encode(public_key.export_key("DER")).decode()
        data = {"user": user, "sign": sign}
        data = encryptsys.encrypt_data(json.dumps(data))
        msg = {"server_name": server, "nonce": nonce_rpl.hex(), "hmac": hmac.hex(), "iv": encryptsys.iv, "data": data}
        self.network.send(json.dumps(msg))
        recv = self.network.receive()
        print("Recv:", recv)
        return
        
