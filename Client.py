import bcrypt
from cryptography.fernet import Fernet
import binascii
import requests

# Change the URL to the actual server URL
login_server_url = "http://127.0.0.1:8000/login"
register_server_url = "http://127.0.0.1:8000/register"

# Encrypt information with two layers
# Encrypt the password in step 1
# Generate a random salt
salt = bcrypt.gensalt()
# Use the generated salt to hash the password at level 1
# Generate a key to create a random key for Fernet
fernet_key = Fernet.generate_key()
# Create a random key
key = Fernet(fernet_key)
# Use the generated Fernet key to encrypt the password at level 2

# Convert salt and key to hex format for transmission
salt_hex = binascii.hexlify(salt).decode()
key_hex = binascii.hexlify(fernet_key).decode()

# Send account information, password, password salt, and Fernet password
def register():
    # Values for a row provided as a tuple
    username_input = input("Enter a new username:")
    password_input = input("Enter a new password:")
    # Use the generated salt to hash the password at level 1
    password_lv1 = bcrypt.hashpw(password_input.encode(), salt)
    password_lv2 = key.encrypt(password_lv1)
    # Create a dictionary containing input values
    payload = {"username_input": username_input, "password_input": password_lv2, "salt": salt_hex, "key": key_hex}
    # Encode client_key_hex back to bytes and then create client_key = Fernet(fernet_key) to get the actual key

    # Send a POST request to the FastAPI server with JSON data
    response = requests.post(register_server_url, json=payload)

# Send account and password information
# Input values you want to send to the server
def login():
    username_input = input("Enter your username:")
    password_input = input("Enter your password:")
    # Use the generated salt to hash the password at level 1
    password_lv1 = bcrypt.hashpw(password_input.encode(), salt)
    password_lv2 = key.encrypt(password_lv1)
    # Create a dictionary containing input values
    payload = {"username_input": username_input, "password_input": password_lv2}
    # Encode client_key_hex back to bytes and then create client_key = Fernet(fernet_key) to get the actual key

    # Send a POST request to the FastAPI server with JSON data
    response = requests.post(login_server_url, json=payload)

def main():
    choice = int(input("Enter 0 to register or 1 to login: "))
    if choice == 0:
        register()
    elif choice == 1:
        login()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
