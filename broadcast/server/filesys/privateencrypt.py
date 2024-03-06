from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes

class AsymmetricEncryptionSystem:
    def __init__(self, rsa_key_pair, aes_key):
        self.rsa_key_pair = rsa_key_pair
        self.aes_key = aes_key

    def encrypt(self, plaintext, rsa_public_key):
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC)
        aes_iv = aes_cipher.iv
        encrypted_plaintext = aes_cipher.encrypt(pad(plaintext.encode(), AES.block_size))

        sha256_hash = SHA256.new()
        sha256_hash.update(encrypted_plaintext)
        aes_hash = sha256_hash.digest()
        aes_hash = bytes([a ^ b for a, b in zip(aes_hash, aes_iv+aes_iv)])

        rsa_cipher = PKCS1_v1_5.new(rsa_public_key)

        # Encrypt the AES hash using the public key of A
        encrypted_aes_hash = rsa_cipher.encrypt(aes_hash)

        encrypted_aes_iv = rsa_cipher.encrypt(aes_iv)

        return b64encode(encrypted_aes_hash + encrypted_aes_iv + encrypted_plaintext).decode()

    def decrypt(self, encrypted_data):
        if(not self.verify_hash(encrypted_data)):
            return None
        encrypted_data = b64decode(encrypted_data)
        encrypted_aes_iv = encrypted_data[256:512]
        encrypted_plaintext = encrypted_data[512:]

        rsa_cipher = PKCS1_v1_5.new(self.rsa_key_pair)
        aes_iv = rsa_cipher.decrypt(encrypted_aes_iv, None)

        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, aes_iv)
        decrypted_plaintext = aes_cipher.decrypt(encrypted_plaintext)
        decrypted_plaintext = unpad(decrypted_plaintext, AES.block_size)

        return decrypted_plaintext.decode()

    def verify_hash(self, encrypted_data):
        encrypted_data = b64decode(encrypted_data)
        encrypted_hash = encrypted_data[:256]
        encrypted_aes_iv = encrypted_data[256:512]
        plaintext = encrypted_data[512:]
        sha256_hash = SHA256.new()
        sha256_hash.update(plaintext)
        plaintext_hash = sha256_hash.digest()

        rsa_cipher = PKCS1_v1_5.new(self.rsa_key_pair)
        try:
            decrypted_hash = rsa_cipher.decrypt(encrypted_hash, None)
            aes_iv = rsa_cipher.decrypt(encrypted_aes_iv, None)
        except:
           return False 
        decrypted_hash = bytes([a ^ b for a, b in zip(decrypted_hash, aes_iv+aes_iv)])
        return plaintext_hash == decrypted_hash
