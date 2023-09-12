import bcrypt
from cryptography.fernet import Fernet
import binascii
import requests
import time
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

class Login(BaseModel):
    username_input: str
    password_input: str
    salt: str
    key: str

class Register(BaseModel):
    username_input: str
    password_input: str
    salt: str
    key: str

@app.post("/register")
async def RegisterInformation(Register_data: Register):
    user_register = Register_data.username_input
    password_register = Register_data.password_input
    salt_register = Register_data.salt
    key_register = Register_data.key
    print("Received salt_register information: ", salt_register)
    print("Received key_register information: ", key_register)

    try:
        connection = mysql.connector.connect(
            user="root",
            password="123456",
            host="localhost",
            database="login",
        )

        mycursor = connection.cursor()

        Cmd_register = ("INSERT INTO `login`.`data`(`user`, `password`, `salt`, `key`) "
                        "VALUES (%s, %s, %s, %s)")
        val_register = (user_register, password_register, salt_register, key_register)

        mycursor.execute(Cmd_register, val_register)

        connection.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()

    finally:
        mycursor.close()
        connection.close()

@app.post("/login")
async def LoginInformation(Login_data: Login):
    user_login = Login_data.username_input
    password_login = Login_data.password_input
    salt_login = Login_data.salt
    key_login = Login_data.key
    print("Received salt_login information: ", salt_login)
    print("Received key_login information: ", key_login)

    try:
        connection = mysql.connector.connect(
            user="root",
            password="123456",
            host="localhost",
            database="login",
        )

        mycursor = connection.cursor()

        Cmd_Login = ("SELECT `password`, `salt`, `key` FROM `login`.`data` WHERE `user` = %s")
        val_login = (user_login,)

        mycursor.execute(Cmd_Login, val_login)
        result = mycursor.fetchall()
        if result:
            datarow = result[0]
            password_find_lv2_hex = datarow[0]
            salt_find_hex = datarow[1]
            key_find_hex = datarow[2]
            print("Salt retrieved from the SQL matches the registration: ", salt_find_hex)
            print("Key retrieved from the SQL matches the registration: ", key_find_hex)

            salt_find_sql = binascii.unhexlify(salt_find_hex)
            key_find_sql = binascii.unhexlify(key_find_hex)
            password_find_lv2_sql = binascii.unhexlify(password_find_lv2_hex)

            key_sql = Fernet(key_find_sql)
            password_lv1_salt_sql = key_sql.decrypt(password_find_lv2_sql)

            salt_find_client = binascii.unhexlify(salt_login)
            key_find_client = binascii.unhexlify(key_login)
            password_login_client = binascii.unhexlify(password_login)

            key_client = Fernet(key_find_client)
            password_lv1_salt_client = key_client.decrypt(password_login_client)

            chuoi3 = str(password_find_lv2_hex)
            print("chuoi3", chuoi3)
            chuoi4 = str(password_login)
            print("chuoi4", chuoi4)
            chuoi1 = str(password_lv1_salt_sql)
            print("chuoi1", chuoi1)
            chuoi2 = str(password_lv1_salt_client)
            print("chuoi2", chuoi2)

            if chuoi3 == chuoi4 and chuoi1 == chuoi2:
                print("Login successful")
                timeout_minutes = 1
                timeout_seconds = timeout_minutes * 60
                start_time = time.time()

                while True:
                    elapsed_time = time.time() - start_time
                    remaining_time = timeout_seconds - elapsed_time

                    if remaining_time <= 0:
                        print("Login time expired. Automatically logging out.")
                        break

                    print(f"Remaining time: {int(remaining_time)} seconds", end="\r")
                    time.sleep(1)

                else:
                    print("Login failed")
            else:
                print("Login failed")
        else:
            print("Account does not exist")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        mycursor.close()
        connection.close()
