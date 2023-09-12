import bcrypt
from cryptography.fernet import Fernet
import binascii
import requests

def main():
    choose = int(input("Choose 0 to register or 1 to log in: "))
    if choose == 0:
        register()
    elif choose == 1:
        login()
    else:
        print("Invalid choice")

def login():
    # Change the URL to the actual server URL
    login_server_url = "http://127.0.0.1:8000/login"

    # Encrypt information with two layers
    # Encrypt the password in step 1
    # Generate a random salt
    salt = bcrypt.gensalt()
    # Use the generated salt to hash the password in level 1
    # Generate a key for Fernet encryption
    fernet_key = Fernet.generate_key()
    # Create a random key
    key = Fernet(fernet_key)
    # Use the generated Fernet key to encrypt the level 1 hashed password

    # Convert salt and key to hex for transmission
    salt_hex = binascii.hexlify(salt).decode()
    key_hex = binascii.hexlify(fernet_key).decode()

    # Send account information, password, password salt, and Fernet password
    # The value of a row is provided as a tuple
    username_input = input("Enter your username:")
    password_input = input("Enter your password:")
    # Use the generated salt to hash the password in level 1
    hashed_password_level1 = bcrypt.hashpw(username_input.encode(), salt)
    encrypted_password_level2 = key.encrypt(hashed_password_level1)
    encrypted_password_level2_hex = binascii.hexlify(encrypted_password_level2).decode()
    # Create a dictionary containing input values
    # The payload should match the class structure, for example:
    # class InformationUser(BaseModel):
    #     client_user: str
    #     client_password: str
    payload = {"client_user": username_input, "client_password": encrypted_password_level2_hex, "salt": salt_hex, "key": key_hex}
    print("Sent salt for login ", salt_hex)
    print("Sent key for login ", key_hex)

    # Send a POST request to the FastAPI server with JSON data
    response = requests.post(login_server_url, json=payload)

def register():
    # Change the URL to the actual server URL
    register_server_url = "http://127.0.0.1:8000/register"

    # Encrypt information with two layers
    # Encrypt the password in step 1
    # Generate a random salt
    salt = bcrypt.gensalt()
    # Use the generated salt to hash the password in level 1
    # Generate a key for Fernet encryption
    fernet_key = Fernet.generate_key()
    # Create a random key
    key = Fernet(fernet_key)
    # Use the generated Fernet key to encrypt the level 1 hashed password

    # Convert salt and key to hex for transmission
    salt_hex = binascii.hexlify(salt).decode()
    key_hex = binascii.hexlify(fernet_key).decode()

    # Send account information, password, password salt, and Fernet password
    # The value of a row is provided as a tuple
    username_register = input("Register a new username:")
    password_register = input("Register a new password: ")
    # Use the generated salt to hash the password in level 1
    hashed_password_level1 = bcrypt.hashpw(password_register.encode(), salt)
    encrypted_password_level2 = key.encrypt(hashed_password_level1)

    encrypted_password_level2_hex = binascii.hexlify(encrypted_password_level2).decode()
    # Create a dictionary containing input values
    # The payload should match the class structure, for example:
    # class InformationUser(BaseModel):
    #     client_user: str
    #     client_password: str
    payload = {"client_user": username_register, "client_password": encrypted_password_level2_hex, "salt": salt_hex, "key": key_hex}
    print("Sent salt for registration ", salt_hex)
    print("Sent key for registration ", key_hex)

    # Send a POST request to the FastAPI server with JSON data
    response = requests.post(register_server_url, json=payload)

if __name__ == "__main__":
    main()
