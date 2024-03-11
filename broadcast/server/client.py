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

    def connect(self, server):
        private_key = self.keysys.load_key(server, "private")
        public_key = self.keysys.load_key(server, "public")
        aes_key = self.keysys.load_key(server, "aes")
        nonce = self.login(server, private_key, aes_key, public_key)
        if nonce is None:
            return
        if not self.login_reply(server, aes_key, nonce):
            return
        return

    def login(self, server, private_key, server_key, public_key):
        replysys = AuthorizationSystem(private_key, server_key)
        encryptsys = SymmetricEncryptionSystem()
        encryptsys.set_key(server_key)
        self.network.connect()
        hs = self.network.socket.recv(1024)
        if len(hs) != 16:
            return None
        sign, hmac, nonce_rpl = replysys.reply_authorize(hs)
        sign = b64encode(sign).decode()
        user = b64encode(public_key.export_key("DER")).decode()
        data = {"user": user, "sign": sign}
        data = encryptsys.encrypt_data(json.dumps(data))
        msg = {"server_name": server, "nonce": nonce_rpl.hex(), "hmac": hmac.hex(), "iv": encryptsys.iv, "data": data}
        self.network.send(json.dumps(msg))
        return hs + nonce_rpl
    
    def login_reply(self, server, aes_key, nonce):
        recv = self.network.receive()
        try:
            rt = json.loads(recv)
            server_name = rt["server_name"]
            iv = rt["iv"]
            data = rt["data"]
        except:
            return False
        if server_name != server:
            return False
        symsys = SymmetricEncryptionSystem()
        symsys.set_key(server_key, iv)
        try:
            data = json.loads(symsys.decrypt_data(data))
            user = data["user"]
            sign = data["sign"]
        except:
            return False
        trust_list = self.trustsys.load_trusted_servers(server)
        if user not in trust_list:
            return False
        if not AuthorizationSystem.authorize_user(nonce, sign, b64decode(user.encode())):
            return False
        return True
