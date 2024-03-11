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

    def _encrypt_data(self, data, encrypt_key = None):
        if encrypt_key is None:
            encrypt_key = self.encryption_key
        cipher = AES.new(encrypt_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        return cipher.iv + encrypted_data

    def _decrypt_data(self, encrypted_data, encrypt_key = None):
        if encrypt_key is None:
            encrypt_key = self.encryption_key
        iv = encrypted_data[:AES.block_size]
        data = encrypted_data[AES.block_size:]
        cipher = AES.new(encrypt_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
        return decrypted_data

    def save_key(self, key_name, key, keytype):
        encrypted_key = self._encrypt_data(key)
        file_path = os.path.join(self.directory, f"{key_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data_dict = json.load(file)
            data_dict[keytype] = encrypted_key.hex()
        else:
            data_dict = {keytype: encrypted_key.hex()}

        with open(file_path, 'w') as file:
            json.dump(data_dict, file)

    def load_key(self, key_name, keytype):
        file_path = os.path.join(self.directory, f"{key_name}.json")
        try:
            with open(file_path, 'r') as file:
                encrypted_key = bytes.fromhex(json.load(file)[keytype])
                return self._decrypt_data(encrypted_key)
        except FileNotFoundError:
            return None

    def change_encryption_key(self, new_encryption_key):
        # Re-encrypt all keys with the new encryption key
        for key_file in os.listdir(self.directory):
            file_path = os.path.join(self.directory, key_file)
            with open(file_path, 'r') as file:
                keys = json.load(file)
            with open(file_path, 'w') as file:
                json.dump({keytype: (self._encrypt_data(self._decrypt_data(bytes.fromhex(keys[keytype])), new_encryption_key)).hex() for keytype in keys}, file)
        
        # Update the encryption key
        self.encryption_key = new_encryption_key

    def change_key(self, key_name, new_key, keytype):
        self.save_key(key_name, new_key, keytype)

    @staticmethod
    def generate_aes_key(password, salt):
        key = PBKDF2(password, salt, dkLen=32)
        return key

