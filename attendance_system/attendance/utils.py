from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    return key

def encrypt_url(url):
    key = generate_key()
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(url.encode())
    return cipher_text.decode(), key.decode()

def decrypt_url(cipher_text, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text.encode())
    return plain_text.decode()