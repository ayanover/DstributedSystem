#!/usr/bin/env python3
import signal
import sys

import requests
import json
import time
import uuid
import argparse
import threading
import logging
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('device')


class MathDevice:
    def __init__(self, device_type, auth_token, server_url):
        # Device identity
        self.device_id = str(uuid.uuid4())
        self.device_type = device_type

        # Server information
        self.server_url = server_url.rstrip('/')
        self.server_public_key = None

        # Authentication
        self.auth_token = auth_token

        # Keys and encryption
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Session information
        self.session_key = None
        self.running = False

        # Set up supported operations based on device type
        self.operations = self._get_operations()

    def _get_operations(self):
        """Define the mathematical operations this device supports based on type"""
        operations = {}

        if self.device_type == "adder":
            operations["add"] = lambda x, y: x + y

        elif self.device_type == "subtractor":
            operations["subtract"] = lambda x, y: x - y

        elif self.device_type == "multiplier":
            operations["multiply"] = lambda x, y: x * y

        elif self.device_type == "divider":
            operations["divide"] = lambda x, y: x / y if y != 0 else "Error: Division by zero"

        elif self.device_type == "calculator":
            operations["add"] = lambda x, y: x + y
            operations["subtract"] = lambda x, y: x - y
            operations["multiply"] = lambda x, y: x * y
            operations["divide"] = lambda x, y: x / y if y != 0 else "Error: Division by zero"
            operations["power"] = lambda x, y: x ** y

        elif self.device_type == "advanced":
            operations["add"] = lambda x, y: x + y
            operations["subtract"] = lambda x, y: x - y
            operations["multiply"] = lambda x, y: x * y
            operations["divide"] = lambda x, y: x / y if y != 0 else "Error: Division by zero"
            operations["power"] = lambda x, y: x ** y
            operations["modulo"] = lambda x, y: x % y if y != 0 else "Error: Modulo by zero"
            operations["factorial"] = lambda x, _: self._factorial(x)

        return operations

    def _factorial(self, n):
        """Calculate factorial for advanced device"""
        if not isinstance(n, int) or n < 0:
            return "Error: Factorial requires non-negative integer"
        if n == 0:
            return 1
        return n * self._factorial(n - 1)

    def get_server_public_key(self):
        """Get the server's public key"""
        try:
            response = requests.get(f"{self.server_url}/server-key")
            if response.status_code == 200:
                self.server_public_key = serialization.load_pem_public_key(
                    response.json()["publicKey"].encode()
                )
                logger.info("Retrieved server public key")
                return True
            else:
                logger.error(f"Failed to get server public key: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error getting server public key: {str(e)}")
            return False

    def encrypt_with_server_key(self, data):
        if not self.server_public_key:
            raise Exception("Server public key not available")

        try:
            # Serialize the data to JSON and encode to bytes
            json_data = json.dumps(data).encode()

            # Generate a random 256-bit AES key
            aes_key = os.urandom(32)

            # Encrypt the JSON data with AES
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Pad the plaintext to be a multiple of 16 bytes
            padding_length = 16 - (len(json_data) % 16)
            padded_data = json_data + bytes([padding_length]) * padding_length

            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            # Encrypt the AES key with RSA
            encrypted_key = self.server_public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Encode components to base64 for transmission
            encrypted_payload = {
                'encrypted_key': base64.b64encode(encrypted_key).decode(),
                'iv': base64.b64encode(iv).decode(),
                'ciphertext': base64.b64encode(ciphertext).decode()
            }

            return encrypted_payload

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise Exception(f"Encryption failed: {str(e)}")

    def decrypt_with_private_key(self, encrypted_data):
        """Decrypt data with our private key"""
        encrypted_bytes = base64.b64decode(encrypted_data)

        # RSA decryption with OAEP padding
        decrypted = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return json.loads(decrypted.decode())

    def encrypt_with_session_key(self, data):
        """Encrypt data with the session key using AES"""
        if not self.session_key:
            raise Exception("Session key not established")

        try:
            # Convert data to JSON and then to bytes
            plaintext = json.dumps(data).encode()

            # Use only the first 32 bytes of the session key for AES-256
            # If session key is a string, encode it first
            if isinstance(self.session_key, str):
                key = self.session_key.encode('utf-8')
            else:
                key = self.session_key

            # Ensure key is exactly 32 bytes (256 bits)
            if len(key) > 32:
                key = key[:32]
            elif len(key) < 32:
                # Pad key if necessary (shouldn't happen with UUID)
                key = key + b'\0' * (32 - len(key))

            # Generate a random IV (Initialization Vector)
            iv = os.urandom(16)  # 16 bytes for CBC mode

            # Create the cipher with the key and IV
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv)
            )
            encryptor = cipher.encryptor()

            # Pad the plaintext to be a multiple of 16 bytes (AES block size)
            padding_length = 16 - (len(plaintext) % 16)
            padded_data = plaintext + bytes([padding_length]) * padding_length

            # Encrypt the data
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            # Combine IV and ciphertext and encode to base64
            encrypted = base64.b64encode(iv + ciphertext).decode()

            return encrypted
        except Exception as e:
            logger.error(f"Error encrypting with session key: {str(e)}")
            raise Exception(f"Error encrypting with session key: {str(e)}")

    def decrypt_with_session_key(self, encrypted_data):
        """Decrypt data with the session key using AES"""
        if not self.session_key:
            raise Exception("Session key not established")

        try:
            # Use only the first 32 bytes of the session key to match server
            key = self.session_key.encode()[:32]

            # Decode from base64
            encrypted = base64.b64decode(encrypted_data)

            # Extract IV and ciphertext
            iv = encrypted[:16]
            ciphertext = encrypted[16:]

            # Create the cipher with the key and IV
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv)
            )
            decryptor = cipher.decryptor()

            # Decrypt the data
            plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            padding_length = plaintext_padded[-1]
            plaintext = plaintext_padded[:-padding_length]

            return json.loads(plaintext.decode())
        except Exception as e:
            logger.error(f"Error decrypting with session key: {str(e)}")
            raise

    def register(self):
        """Register the device with the backend server"""
        logger.info(f"Registering {self.device_type} device ({self.device_id})...")

        # First get the server's public key if we don't have it
        if not self.server_public_key:
            if not self.get_server_public_key():
                return False

        # Create registration payload
        registration_payload = {
            "deviceInfo": {
                "deviceId": self.device_id,
                "publicKey": self.public_key_pem,
                "metadata": {
                    "type": self.device_type,
                    "manufacturer": "Virtual Device Corp",
                    "model": f"MATH-{self.device_type.upper()}-1000",
                    "version": "1.0.0"
                },
                "operations": list(self.operations.keys())  # The server maps this to capabilities
            },
            "authToken": self.auth_token
        }

        # Encrypt the payload with the server's public key
        encrypted_payload = self.encrypt_with_server_key(registration_payload)

        # In your register() method in the IoTDevice class
        try:
            # Send registration request
            response = requests.post(
                f"{self.server_url}/register-device/",  # Make sure this matches your server endpoint
                json={"data": encrypted_payload}
            )

            if response.status_code == 200:
                # Check response format - add debugging
                logger.debug(f"Response content: {response.text}")

                # Get the response data
                response_data = response.json()

                # Check what format the response is in
                if isinstance(response_data, dict) and "encrypted" in response_data:
                    encrypted_response = response_data["encrypted"]
                else:
                    # Assume the entire response is encrypted
                    encrypted_response = response_data

                # Decrypt the response with our private key
                decrypted_data = self.decrypt_with_private_key(encrypted_response)

                # Store the session key
                self.session_key = decrypted_data["sessionKey"]
                logger.info(f"Registration successful. Session key received.")
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False

    def get_pending_commands(self):
        """Get pending commands from the server"""
        if not self.session_key:
            logger.warning("Cannot poll for commands: Not registered")
            return []

        try:
            response = requests.get(
                f"{self.server_url}/devices/{self.device_id}/pending-commands"
            )

            if response.status_code == 200:
                # Check if response is encrypted
                if "data" in response.json():
                    # Decrypt the data
                    commands_data = self.decrypt_with_session_key(response.json()["data"])
                    return commands_data.get("commands", [])
                else:
                    # Fallback for unencrypted response
                    return response.json().get("commands", [])
            else:
                logger.warning(f"Failed to get pending commands: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting pending commands: {str(e)}")
            return []

    def execute_command(self, command):
        """Execute a command received from the server"""
        logger.info(f"Executing command: {command['name']} (ID: {command['id']})")

        try:
            if command["name"] not in self.operations:
                return {
                    "status": "failed",
                    "error": f"Operation '{command['name']}' not supported by this device"
                }

            operation = self.operations[command["name"]]
            params = command["params"]

            # Special case for factorial which only takes one parameter
            if command["name"] == "factorial":
                result = operation(params["num1"], None)
            else:
                # Regular case for operations that take two parameters
                result = operation(params["num1"], params["num2"])

            return {
                "status": "completed",
                "result": result
            }

        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def report_command_result(self, command_id, result):
        """Report the result of a command back to the server"""
        if not self.session_key:
            logger.warning("Cannot report result: Not registered")
            return False

        try:
            # Encrypt the result data
            encrypted_data = self.encrypt_with_session_key(result)

            # Send the result
            response = requests.post(
                f"{self.server_url}/commands/{command_id}/update",
                json={
                    "deviceId": self.device_id,
                    "data": encrypted_data
                }
            )

            if response.status_code == 200:
                logger.info(f"Result reported successfully")
                return True
            else:
                logger.warning(f"Failed to report result: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error reporting result: {str(e)}")
            return False

    def start(self):
        """Start the device simulation"""
        if self.running:
            return

        # Register the device
        if not self.register():
            logger.error("Registration failed. Cannot start device.")
            return

        self.running = True
        logger.info(f"{self.device_type.capitalize()} device started")

        # Start the command polling loop in a separate thread
        threading.Thread(target=self._polling_loop, daemon=True).start()

    def _polling_loop(self):
        """Background thread for polling commands"""
        while self.running:
            try:
                # Get pending commands
                commands = self.get_pending_commands()

                # Execute each command and report results
                for command in commands:
                    result = self.execute_command(command)
                    self.report_command_result(command["id"], result)

                # Sleep before polling again
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in polling loop: {str(e)}")
                time.sleep(10)  # Longer delay after error

    def stop(self):
        """Stop the device simulation"""
        logger.info(f"Stopping {self.device_type} device...")
        self.running = False

        # Try to deregister
        deregister(self)

        logger.info(f"{self.device_type.capitalize()} device stopped")


def deregister(self):
    """Deregister the device from the server when shutting down"""
    if not self.session_key:
        logger.warning("Cannot deregister: Not registered")
        return False

    logger.info(f"Deregistering {self.device_type} device ({self.device_id})...")

    try:
        # Create a deregistration request
        data = {
            "status": "offline",
            "timestamp": time.time()
        }

        # Encrypt the data with the session key
        encrypted_data = self.encrypt_with_session_key(data)

        # Send the deregistration request
        response = requests.post(
            f"{self.server_url}/devices/{self.device_id}/deregister",
            json={
                "deviceId": self.device_id,
                "data": encrypted_data
            }
        )

        if response.status_code == 200:
            logger.info("Device successfully deregistered")
            return True
        else:
            logger.warning(f"Failed to deregister device: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error deregistering device: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Math Device Simulator")
    parser.add_argument("--type", choices=["adder", "subtractor", "multiplier", "divider", "calculator", "advanced"],
                        default="calculator", help="Type of mathematical device to simulate")
    parser.add_argument("--token", required=True, help="Authorization token for device registration")
    parser.add_argument("--server", default="http://localhost:8000/api", help="Server URL")
    args = parser.parse_args()

    try:
        # Create and start the device
        device = MathDevice(args.type, args.token, args.server)

        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal, stopping device...")
            device.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        device.start()

        # Keep the main thread alive
        try:
            # Cross-platform solution instead of signal.pause()
            while device.running:
                time.sleep(1)
        except KeyboardInterrupt:
            device.stop()

    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()