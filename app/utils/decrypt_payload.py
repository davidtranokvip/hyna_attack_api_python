from Crypto.Util.Padding import unpad
from cryptography.hazmat.primitives.asymmetric import padding
from Crypto.Cipher import AES
from binascii import unhexlify
import base64
import json

def decrypt_payload(data, private_key):

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