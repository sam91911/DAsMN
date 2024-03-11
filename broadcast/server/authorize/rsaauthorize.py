from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
import base64

class AuthorizationSystem:
    def __init__(self, rsa_key, server_key):
        self.rsa_key = rsa_key
        self.server_key = server_key

    @staticmethod
    def generate_nonce():
        return get_random_bytes(16)

    @staticmethod
    def authorize_user(nonce_send, signature, nonce_receive, rsa_public_key):
        if isinstance(rsa_public_key, str) or isinstance(rsa_public_key, bytes):
            rsa_public_key = RSA.import_key(rsa_public_key)
        cipher_rsa = PKCS1_v1_5.new(rsa_public_key)
        hashed_data = SHA256.new(nonce_send+nonce_receive)
        return cipher_rsa.verify(hashed_data, signature)

    @staticmethod
    def hmac_check(nonce_send, hmac_value, nonce_receive, server_key):
        return AuthorizationSystem.hmac(nonce_send, nonce_receive, server_key) == hmac_value

    @staticmethod
    def hmac(nonce_send, nonce_receive, server_key):
        hmac_obj = HMAC.new(server_key, digestmod=SHA256)
        hmac_obj.update(nonce_send+nonce_receive)
        return hmac_obj.digest()

    def reply_authorize(self, nonce_send):
        cipher_rsa = PKCS1_v1_5.new(self.rsa_key)
        nonce_reply = self.generate_nonce()
        hashed_data = SHA256.new(nonce_send+nonce_reply)
        signature = cipher_rsa.sign(hashed_data)
        hmac_value = self.hmac(nonce_send, nonce_reply, self.server_key)
        return signature, hmac_value, nonce_reply


