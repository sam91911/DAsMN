from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64

class AuthorizationSystem:
    def __init__(self, rsa_key):
        self.rsa_key = rsa_key

    @staticmethod
    def generate_nonce():
        return get_random_bytes(16)

    @staticmethod
    def authorize_user(nonce_send, signature, nonce_receive, rsa_public_key):
        cipher_rsa = PKCS1_v1_5.new(rsa_public_key)
        hashed_data = SHA256.new(nonce_send+nonce_receive)
        return cipher_rsa.verify(hashed_data, signature)

    def reply_authorize(self, nonce_send):
        cipher_rsa = PKCS1_v1_5.new(self.rsa_key)
        nonce_reply = self.generate_nonce()
        hashed_data = SHA256.new(nonce_send+nonce_reply)
        signature = cipher_rsa.sign(hashed_data)
        return signature, nonce_reply


