import bcrypt
import os
from getpass import getpass
import base64
import sys
import time
import codecs

currect_file_location = os.path.dirname(os.path.realpath(__file__))
os.chdir(currect_file_location + "/users")

print("Users:")
for file in os.listdir():
    print(file)
    print()

username = input("Username: ")
password = getpass("Password: ")


def hash_password(password):
    salt = bcrypt.gensalt(13)
    hashed_password = bcrypt.hashpw(password.encode("UTF-8"), salt)
    return hashed_password


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("UTF-8"), hashed_password)


def find_user(username, password):
    if os.path.isfile(username):
        user_file = open(username, "r")
        user_password_hash = user_file.read()
        user_file.close()
        if check_password(password, user_password_hash.encode("UTF-8")):
            return True
        else:
            return False
    else:
        return False


def new_user(new_username, new_password, username, password):
    if find_user(username, password):
        new_password_hash = hash_password(new_password)
        print("New password hash: " + new_password_hash.decode("UTF-8"))
        new_user_file = open(new_username, "w")
        new_user_file.write(new_password_hash.decode("UTF-8"))
        new_user_file.close()
    else:
        print("Your current user does not exist!")


def user_settings():
    print("""
    1 - Change Username
    2 - Change Password
    3 - Delete User
    4 - Return to main menu
    """)
    cmd = input("Command: ")
    if cmd == "1":
        os.rename(username, input("New Username: "))
    elif cmd == "2":
        if find_user(username, password) == True:
            newpassword = getpass("Enter your new password: ")
            newpassword2 = getpass("Enter your new password again: ")
            if newpassword == newpassword2:
                new_password_hash = hash_password(newpassword)
                user_file = open(username, "w")
                user_file.write(new_password_hash.decode("UTF-8"))
                user_file.close()
                print("Password changed!")
            else:
                print("Passwords do not match!")
        else:
            print("Your user does not exist!")
    elif cmd == "3":
        deleted_user = input("Enter the username of the user you want to delete: ")
        if os.path.exists(deleted_user):
            os.remove(deleted_user)
            print("User deleted!")
        else:
            print("User does not exist!")
    elif cmd == "4":
        print("Returning to main menu")
    else:
        print("Invalid command!")


def selector():
    print("""
        1 - Create a new user
        2 - User settings
        3 - PyArmor Deobfuscator
        4 - Development Tools Deobfuscator
        3 - Today's Schedule
        4 - Math Notes
        5 - Pythaoras Theorem
        6 - Password Stealer
        7 - Random Number Generator
        8 - Website Scraper
        9 - File Encrypter
        exit - Exits the code
        """)
    cmd = input("Command: ")

    if cmd == "exit":
        print("Goodbye!")
        sys.exit()
    elif cmd == "1":
        new_username = input("Enter a new username: ")
        new_password = getpass("Enter a new password: ")
        new_user(new_username, new_password, password)
        print("Verifying...")
        if find_user(new_username, new_password):
            print("User created!")
        else:
            print("User not created!")
    elif cmd == "2":
        user_settings()
    elif cmd == "3":
        print("I'm still working on this")
    elif cmd == "4":
        magic = input("Magic: ")
        love = input("Love: ")
        god = input("God: ")
        destiny = input("Destiny: ")
        joy = 'rot13'
        trust = magic + codecs.decode(love, joy) + god + codecs.decode(destiny, joy)
        print(base64.b64decode(trust))
    elif cmd == "5":
        print("I'm still working on this")
    elif cmd == "6":
        print("I'm still working on this")
    elif cmd == "7":
        print("I'm still working on this")
    elif cmd == "8":
        print("I'm still working on this")
    elif cmd == "9":
        print("I'm still working on this")
    else:
        print("Invalid command! For help, type 'help'")


if not find_user(username, password):
    print("Incorrect username or password!")
else:
    print("Correct password!\nAccessing system...")
    while True:
        selector()

