#!/usr/bin/env python3
import requests
import json
import uuid
import time
import argparse
import logging
import base64
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('device')


class MathDevice:
    """Simulates a mathematical device that can perform various operations"""

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