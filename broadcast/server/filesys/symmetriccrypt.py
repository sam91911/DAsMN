from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

class SymmetricEncryptionSystem:
    def __init__(self):
        self.key = None
        self.cipher = None

    @staticmethod
    def generate_key(password = None, salt = None):
        if password and salt:
            key = PBKDF2(password, salt, dkLen=32)
        else:
            key = get_random_bytes(32)
        return key

    def set_key(self, key, iv = None):
        self.key = key
        if iv is None:
            self.cipher = AES.new(self.key, AES.MODE_CBC)
        else:
            self.cipher = AES.new(self.key, AES.MODE_CBC, b64decode(iv))

    def encrypt_data(self, data):
        encrypted_data = self.cipher.encrypt(pad(data.encode(), AES.block_size))
        return b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data):
        encrypted_data = b64decode(encrypted_data)
        decrypted_data = unpad(self.cipher.decrypt(encrypted_data), AES.block_size)
        return decrypted_data.decode()

    def encrypt_symmetric_key(self, public_key, symmetric_key):
        cipher_rsa = PKCS1_v1_5.new(public_key)
        encrypted_key = cipher_rsa.encrypt(symmetric_key)
        iv = b64encode(self.cipher.iv).decode('utf-8')
        return b64encode(encrypted_key).decode(), iv

    @staticmethod
    def decrypt_symmetric_key(private_key, encrypted_key):
        cipher_rsa = PKCS1_v1_5.new(private_key)
        encrypted_key = b64decode(encrypted_key)
        symmetric_key = cipher_rsa.decrypt(encrypted_key, None)
        return symmetric_key

    def derive_key(self, salt, iterations):
        return PBKDF2(self.key, salt, dkLen=32, count=iterations, hmac_hash_module=SHA256)


