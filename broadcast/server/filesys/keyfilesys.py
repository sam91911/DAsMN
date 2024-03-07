import os
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class KeyFileSystem:
    def __init__(self, directory, encryption_key, is_password=False, use_saved_salt=True):
        self.directory = directory
        self.salt_file = os.path.join(directory, "salt.json")
        os.makedirs(directory, exist_ok=True)
        
        if is_password:
            if use_saved_salt:
                if os.path.exists(self.salt_file):
                    with open(self.salt_file, 'r') as f:
                        self.salt = bytes.fromhex(json.load(f)['salt'])
                else:
                    self.salt = get_random_bytes(16)
                    with open(self.salt_file, 'w') as f:
                        json.dump({'salt': self.salt.hex()}, f)
            else:
                self.salt = get_random_bytes(16)
                with open(self.salt_file, 'w') as f:
                    json.dump({'salt': self.salt.hex()}, f)
            self.encryption_key = self.generate_aes_key(encryption_key.encode(), self.salt)
        else:
            self.encryption_key = encryption_key

    def _encrypt_data(self, data):
        cipher = AES.new(self.encryption_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return cipher.iv + encrypted_data

    def _decrypt_data(self, encrypted_data):
        iv = encrypted_data[:AES.block_size]
        data = encrypted_data[AES.block_size:]
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
        return decrypted_data.decode()

    def save_key(self, key_name, key):
        encrypted_key = self._encrypt_data(key)
        file_path = os.path.join(self.directory, f"{key_name}.json")
        with open(file_path, 'w') as file:
            json.dump({'key': encrypted_key.hex()}, file)

    def load_key(self, key_name):
        file_path = os.path.join(self.directory, f"{key_name}.json")
        try:
            with open(file_path, 'r') as file:
                encrypted_key = bytes.fromhex(json.load(file)['key'])
                return self._decrypt_data(encrypted_key)
        except FileNotFoundError:
            return None

    def change_encryption_key(self, new_encryption_key):
        # Re-encrypt all keys with the new encryption key
        for key_file in os.listdir(self.directory):
            file_path = os.path.join(self.directory, key_file)
            with open(file_path, 'r') as file:
                encrypted_key = bytes.fromhex(json.load(file)['key'])
                decrypted_key = self._decrypt_data(encrypted_key)
                new_encrypted_key = self._encrypt_data(decrypted_key)
            with open(file_path, 'w') as file:
                json.dump({'key': new_encrypted_key.hex()}, file)
        
        # Update the encryption key
        self.encryption_key = new_encryption_key

    def change_key(self, key_name, new_key):
        encrypted_key = self._encrypt_data(new_key)
        file_path = os.path.join(self.directory, f"{key_name}.json")
        with open(file_path, 'w') as file:
            json.dump({'key': encrypted_key.hex()}, file)

    @staticmethod
    def generate_aes_key(password, salt):
        key = PBKDF2(password, salt, dkLen=32)
        return key

