"""Encryption utilities for file storage."""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os


def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
    """Generate encryption key from password."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_file(file_path: str, key: bytes) -> bytes:
    """Encrypt a file."""
    fernet = Fernet(key)
    with open(file_path, "rb") as f:
        file_data = f.read()
    encrypted_data = fernet.encrypt(file_data)
    return encrypted_data


def decrypt_file(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt a file."""
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data


def encrypt_string(data: str, key: bytes) -> str:
    """Encrypt a string."""
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()


def decrypt_string(encrypted_data: str, key: bytes) -> str:
    """Decrypt a string."""
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(base64.b64decode(encrypted_data))
    return decrypted_data.decode()

