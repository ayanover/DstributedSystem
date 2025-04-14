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
    """Decrypt data using the server's private key and AES"""
    try:
        # Verify we have a dictionary with the expected components
        if not isinstance(encrypted_data,
                          dict) or 'encrypted_key' not in encrypted_data or 'iv' not in encrypted_data or 'ciphertext' not in encrypted_data:
            logger.error(f"Invalid encrypted data format: {encrypted_data}")
            raise ValueError(
                "Invalid encrypted data format. Expected dictionary with encrypted_key, iv, and ciphertext.")

        # Decode components from base64
        encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])

        # Decrypt the AES key with RSA
        aes_key = SERVER_PRIVATE_KEY.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the data with AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        padding_length = plaintext_padded[-1]
        plaintext = plaintext_padded[:-padding_length]

        # Parse JSON
        return json.loads(plaintext.decode())
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
        # Convert session key to bytes and ensure it's 32 bytes (256 bits)
        if isinstance(session_key, str):
            key = session_key.encode('utf-8')
        else:
            key = session_key

        if len(key) > 32:
            key = key[:32]
        elif len(key) < 32:
            key = key + b'\0' * (32 - len(key))

        # Decode from base64
        decoded_data = base64.b64decode(encrypted_data)

        # Extract IV and ciphertext
        iv = decoded_data[:16]
        ciphertext = decoded_data[16:]

        # Decrypt with AES-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        padding_length = plaintext_padded[-1]
        plaintext = plaintext_padded[:-padding_length]

        # Parse JSON
        return json.loads(plaintext.decode())
    except Exception as e:
        logger.error(f"Error decrypting with session key: {str(e)}")
        raise


def encrypt_with_session_key(data, session_key):
    """Encrypt data using an AES session key"""
    try:
        # Convert data to JSON and then encode to bytes
        json_data = json.dumps(data).encode()

        # Derive a 32-byte (256-bit) key from the session key
        # This ensures the key is exactly the right size for AES-256
        key = session_key.encode()[:32]

        # Generate a random IV
        iv = os.urandom(16)  # 16 bytes for CBC mode

        # Create the cipher with the proper length key and IV
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        )
        encryptor = cipher.encryptor()

        # Pad the plaintext to be a multiple of 16 bytes (AES block size)
        padding_length = 16 - (len(json_data) % 16)
        padded_data = json_data + bytes([padding_length]) * padding_length

        # Encrypt the data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV and ciphertext and encode to base64
        encrypted = base64.b64encode(iv + ciphertext).decode()

        return encrypted
    except Exception as e:
        logger.error(f"Error encrypting with session key: {str(e)}")
        raise