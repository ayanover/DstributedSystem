import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Helper functions for encryption/decryption

def load_server_keys():
    """Load server keys from files or generate if not present"""
    private_key_path = 'server_private_key.pem'
    public_key_path = 'server_public_key.pem'

    try:
        # Try to load existing keys
        if os.path.exists(private_key_path) and os.path.exists(public_key_path):
            with open(private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

            with open(public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )

            logger.info("Loaded existing server keys")
        else:
            # Generate new key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            # Serialize keys to PEM format
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Save keys to files
            with open(private_key_path, 'wb') as f:
                f.write(private_pem)

            with open(public_key_path, 'wb') as f:
                f.write(public_pem)

            logger.info("Generated and saved new server keys")

        return private_key, public_key
    except Exception as e:
        logger.error(f"Error loading/generating server keys: {str(e)}")
        raise


# Global server keys
SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY = load_server_keys()


def get_server_public_key_pem():
    """Get server public key in PEM format"""
    return SERVER_PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')


def decrypt_with_private_key(encrypted_data):
    """Decrypt data using the server's private key"""
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)

        decrypted = SERVER_PRIVATE_KEY.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return json.loads(decrypted.decode())
    except Exception as e:
        logger.error(f"Error decrypting with private key: {str(e)}")
        raise


def encrypt_with_public_key(data, public_key_pem):
    """Encrypt data using a device's public key"""
    try:
        device_public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )

        json_data = json.dumps(data).encode()

        encrypted = device_public_key.encrypt(
            json_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return base64.b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Error encrypting with public key: {str(e)}")
        raise


def decrypt_with_session_key(encrypted_data, session_key):
    """Decrypt data using an AES session key"""
    try:
        # Convert session key from hex to bytes
        key = bytes.fromhex(session_key)

        # Get the encrypted components
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        tag = base64.b64decode(encrypted_data["tag"])

        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return json.loads(plaintext.decode())
    except Exception as e:
        logger.error(f"Error decrypting with session key: {str(e)}")
        raise


def encrypt_with_session_key(data, session_key):
    """Encrypt data using an AES session key"""
    try:
        # Convert session key from hex to bytes
        key = bytes.fromhex(session_key)

        # Generate a random IV
        iv = os.urandom(12)  # 96 bits for GCM

        # Encrypt
        plaintext = json.dumps(data).encode()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag

        return {
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode()
        }
    except Exception as e:
        logger.error(f"Error encrypting with session key: {str(e)}")
        raise