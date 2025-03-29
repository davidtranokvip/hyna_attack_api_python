from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from binascii import unhexlify
import base64
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
private_key_path = os.path.join(BASE_DIR, 'configs', 'private_key.pem')

with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

def decrypt_payload(data):

    encrypted_data = data.get('encryptedData')
    encrypted_key = data.get('encryptedKey')
    iv_base64 = data.get('iv')

    if not all([encrypted_data, encrypted_key, iv_base64]):
        raise ValueError("Missing required encryption fields (encryptedData, encryptedKey, iv)")

    try:
        decoded_key = base64.b64decode(encrypted_key)
        aes_key_hex = private_key.decrypt(
            decoded_key,
            padding.PKCS1v15()
        ).decode('utf-8')
    except Exception as e:
        raise Exception(f"RSA decryption failed: {str(e)}")

    try:
        aes_key_bytes = unhexlify(aes_key_hex)
        iv = base64.b64decode(iv_base64)
        encrypted_bytes = base64.b64decode(encrypted_data)

        cipher = AES.new(aes_key_bytes, AES.MODE_CBC, iv)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        decrypted_data = decrypted_bytes.decode('utf-8')
        payload = json.loads(decrypted_data)
        return payload

    except Exception as e:
        print("AES Decryption Error:", str(e))
        raise Exception(f"AES decryption failed: {str(e)}")