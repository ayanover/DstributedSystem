#!/usr/bin/env python3
import requests
import json
import time
import uuid
import os
import argparse
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class MathDevice:
    def __init__(self, device_type, auth_token, server_url, server_public_key_pem):
        # Device identity
        self.device_id = str(uuid.uuid4())
        self.device_type = device_type

        # Server information
        self.server_url = server_url
        self.server_public_key = serialization.load_pem_public_key(server_public_key_pem.encode())

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
        return n * self._factorial(n-1)

    def encrypt_with_server_key(self, data):
        """Encrypt data with the server's public key"""
        json_data = json.dumps(data).encode()

        # RSA encryption with OAEP padding
        encrypted = self.server_public_key.encrypt(
            json_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return base64.b64encode(encrypted).decode()

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
        """Encrypt data with the session key using AES-GCM"""
        if not self.session_key:
            raise Exception("Session key not established")

        # Convert session key from hex to bytes
        key = bytes.fromhex(self.session_key)

        # Generate a random IV (Initialization Vector)
        iv = os.urandom(12)  # 96 bits for GCM

        # Convert data to JSON and then to bytes
        plaintext = json.dumps(data).encode()

        # Create the cipher with the key and IV
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()

        # Encrypt the data
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get the authentication tag
        tag = encryptor.tag

        return {
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode()
        }

    def decrypt_with_session_key(self, data):
        """Decrypt data with the session key using AES-GCM"""
        if not self.session_key:
            raise Exception("Session key not established")

        # Convert session key from hex to bytes
        key = bytes.fromhex(self.session_key)

        # Decode the received data
        iv = base64.b64decode(data["iv"])
        ciphertext = base64.b64decode(data["ciphertext"])
        tag = base64.b64decode(data["tag"])

        # Create the cipher with the key and IV
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()

        # Decrypt the data
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return json.loads(plaintext.decode())

    def register(self):
        """Register the device with the backend server"""
        print(f"[{self.device_id}] Registering {self.device_type} device...")

        # Create registration payload
        registration_payload = {
            "deviceInfo": {
                "deviceId": self.device_id,
                "publicKey": self.public_key_pem,
                "metadata": {
                    "type": self.device_type,
                    "operations": list(self.operations.keys()),
                    "version": "1.0.0"
                }
            },
            "authToken": self.auth_token
        }

        # Encrypt the payload with the server's public key
        encrypted_payload = self.encrypt_with_server_key(registration_payload)

        try:
            # Send registration request
            response = requests.post(
                f"{self.server_url}/register",
                json={"data": encrypted_payload}
            )

            if response.status_code == 200:
                # Decrypt the response with our private key
                decrypted_data = self.decrypt_with_private_key(response.json())

                # Store the session key
                self.session_key = decrypted_data["sessionKey"]
                print(f"[{self.device_id}] Registration successful")
                return True
            else:
                print(f"[{self.device_id}] Registration failed: {response.text}")
                return False

        except Exception as e:
            print(f"[{self.device_id}] Registration error: {str(e)}")
            return False

    def poll_for_commands(self):
        """Poll the server for commands"""
        if not self.session_key:
            print(f"[{self.device_id}] Cannot poll: Not registered")
            return

        try:
            # Create poll payload
            poll_payload = self.encrypt_with_session_key({
                "timestamp": int(time.time()),
                "deviceId": self.device_id
            })

            # Send poll request
            response = requests.post(
                f"{self.server_url}/poll",
                json={
                    "deviceId": self.device_id,
                    "data": base64.b64encode(json.dumps(poll_payload).encode()).decode()
                }
            )

            if response.status_code == 200:
                data = response.json()

                if "command" in data:
                    encrypted_cmd = json.loads(base64.b64decode(data["command"]).decode())
                    command = self.decrypt_with_session_key(encrypted_cmd)

                    # Execute the command
                    result = self.execute_command(command)

                    # Send back the result
                    self.send_result(command["id"], result)

                return True
            else:
                print(f"[{self.device_id}] Poll failed: {response.text}")
                return False

        except Exception as e:
            print(f"[{self.device_id}] Poll error: {str(e)}")
            return False

    def execute_command(self, command):
        """Execute a command received from the server"""
        print(f"[{self.device_id}] Executing command: {command['name']}")

        try:
            if command["name"] not in self.operations:
                return {
                    "status": "error",
                    "error": f"Operation '{command['name']}' not supported by this device"
                }

            operation = self.operations[command["name"]]

            params = command["params"]

            result = operation(params["num1"], params["num2"] if "num2" in params else None)

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def send_result(self, command_id, result):
        """Send the result of a command back to the server"""
        try:
            result_payload = self.encrypt_with_session_key({
                "commandId": command_id,
                "result": result,
                "timestamp": int(time.time())
            })

            response = requests.post(
                f"{self.server_url}/result",
                json={
                    "deviceId": self.device_id,
                    "data": base64.b64encode(json.dumps(result_payload).encode()).decode()
                }
            )

            if response.status_code == 200:
                print(f"[{self.device_id}] Result sent successfully")
                return True
            else:
                print(f"[{self.device_id}] Failed to send result: {response.text}")
                return False

        except Exception as e:
            print(f"[{self.device_id}] Error sending result: {str(e)}")
            return False

    def start(self):
        """Start the device simulation"""
        if self.running:
            return

        self.running = True

        if not self.register():
            self.running = False
            return

        def polling_loop():
            while self.running:
                self.poll_for_commands()
                time.sleep(5)

        threading.Thread(target=polling_loop, daemon=True).start()
        print(f"[{self.device_id}] {self.device_type.capitalize()} device started")

    def stop(self):
        """Stop the device simulation"""
        self.running = False
        print(f"[{self.device_id}] {self.device_type.capitalize()} device stopped")


def main():
    parser = argparse.ArgumentParser(description="Math Device Simulator")
    parser.add_argument("--server", required=True, help="Backend server URL")
    parser.add_argument("--pubkey", required=True, help="Server's public key in PEM format")
    parser.add_argument("--token", required=True, help="Authorization token for registration")
    parser.add_argument("--count", type=int, default=10, help="Number of devices to simulate")

    args = parser.parse_args()

    with open(args.pubkey, 'r') as f:
        server_public_key = f.read()

    device_types = [
        "adder", "subtractor", "multiplier", "divider",
        "calculator", "advanced"
    ]

    devices = []
    for i in range(args.count):
        device_type = device_types[i % len(device_types)]
        device = MathDevice(device_type, args.token, args.server, server_public_key)
        devices.append(device)
        device.start()

        time.sleep(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all devices...")
        for device in devices:
            device.stop()


if __name__ == "__main__":
    main()