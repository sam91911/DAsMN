from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode

class SignatureSystem:
    def __init__(self, rsa_key_pair):
        self.rsa_key_pair = rsa_key_pair

    def sign(self, data):
        # Calculate the SHA-256 hash of the data
        h = SHA256.new(data.encode())

        # Sign the hash with the private key
        signature = pkcs1_15.new(self.rsa_key_pair).sign(h)
        return b64encode(signature).decode()

    @staticmethod
    def verify(data, signature, rsa_public_key):
        # Calculate the SHA-256 hash of the data
        h = SHA256.new(data.encode())

        # Verify the signature with the provided public key
        try:
            pkcs1_15.new(rsa_public_key).verify(h, b64decode(signature))
            return True
        except (ValueError, TypeError):
            return False

