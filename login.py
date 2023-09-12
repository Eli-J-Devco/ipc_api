import bcrypt
from cryptography.fernet import Fernet
import binascii
import requests

# Change the URL to the actual server URL
server_url_login = "http://127.0.0.1:8000/login"

# Encrypt information using two layers
# Encrypt the password in the first step
# Generate a random salt
salt = bcrypt.gensalt()
# Use the generated salt to hash the password at level 1
# Create a token to generate a random key for Fernet
fernet_key = Fernet.generate_key()
# Generate a random key
key = Fernet(fernet_key)
# Use the Fernet key to encrypt the password at level 2

# Convert salt and key to hexadecimal to send them
salt_hex = binascii.hexlify(salt).decode()
key_hex = binascii.hexlify(fernet_key).decode()

# Send account information, password, password salt, and Fernet password.
# Values for a row provided as a tuple
username_input = input("Enter your username:")
password_input = input("Enter your password:")
# Use the generated salt to hash the password at level 1
hashed_password_lv1 = bcrypt.hashpw(username_input.encode(), salt)
encrypted_password_lv2 = key.encrypt(hashed_password_lv1)
encrypted_password_lv2_hex = binascii.hexlify(encrypted_password_lv2).decode()
# Create a dictionary containing the input values
payload = {"username": username_input, "password": encrypted_password_lv2_hex, "salt": salt_hex, "key": key_hex}
print("Salt sent: ", salt_hex)
print("Key sent: ", key_hex)

# Send a POST request to the FastAPI server with JSON data
response = requests.post(server_url_login, json=payload)
