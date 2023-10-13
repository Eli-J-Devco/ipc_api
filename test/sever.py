# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 
from fastapi import FastAPI ,Request
from pydantic import BaseModel
import mysql.connector
import bcrypt
from cryptography.fernet import Fernet
import binascii
import threading
import time

app = FastAPI()

# Global variable for fernet_key
fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='

# Create a class to receive data from logged in clients
class Login(BaseModel):
    taikhoannhap: str
    matkhaunhap: str

# Create a class to receive data from registered clients
class Register(BaseModel):
    taikhoannhap: str
    matkhaunhap: str

# Create a class to receive data from the delete client
class delete(BaseModel):
    taikhoanxoa: str
# Create a class to receive data from update client
class update(BaseModel):
    taikhoannhap: str
    matkhau_update: str
    matkhau_old: str
# Create a class to receive data from logged in clients
class Read_Modbus_TCP(BaseModel):
    ip:str
    registers_0: str
    registers_1: str
    registers_2: str
    registers_3: str
    registers_4: str
    datetime   : str

tableCode = [
    {'value': '2ZS', 'id': '!'}, {'value': 'X3p', 'id': '“'}, {'value': 'imE', 'id': '#'}, {'value': 'EUT', 'id': '$'},
    {'value': 'XSh', 'id': '%'}, {'value': 'E5P', 'id': '&'}, {'value': 'WEj', 'id': '‘'}, {'value': '45Q', 'id': '('},
    {'value': 'iI1', 'id': ')'}, {'value': 't6x', 'id': '*'}, {'value': 'hd9', 'id': '+'}, {'value': 'jiJ', 'id': ','},
    {'value': 'UPw', 'id': '-'}, {'value': 'AxC', 'id': '.'}, {'value': 'Ywb', 'id': '/'}, {'value': 'aY8', 'id': '0'},
    {'value': 'mLR', 'id': '1'}, {'value': 'qae', 'id': '2'}, {'value': 'Xpg', 'id': '3'}, {'value': 'oS3', 'id': '4'},
    {'value': 'dTN', 'id': '5'}, {'value': 'jSC', 'id': '6'}, {'value': 'Dfz', 'id': '7'}, {'value': 'Sz1', 'id': '8'},
    {'value': 'Qu1', 'id': '9'}, {'value': 'i5E', 'id': ':'}, {'value': 'IQ6', 'id': ';'}, {'value': 'Qnn', 'id': '<'},
    {'value': 'ZPA', 'id': '='}, {'value': 'N9x', 'id': '>'}, {'value': 'oiI', 'id': '?'}, {'value': 'yU3', 'id': '@'},
    {'value': '46o', 'id': 'A'}, {'value': '7nE', 'id': 'B'}, {'value': 'wuQ', 'id': 'C'}, {'value': 'O1O', 'id': 'D'},
    {'value': 'SKy', 'id': 'E'}, {'value': 'r1H', 'id': 'F'}, {'value': 'aUW', 'id': 'G'}, {'value': 'Tew', 'id': 'H'},
    {'value': 'chh', 'id': 'I'}, {'value': '7FA', 'id': 'J'}, {'value': 'ekK', 'id': 'K'}, {'value': 'Ewp', 'id': 'L'},
    {'value': 'Oxa', 'id': 'M'}, {'value': 'T6g', 'id': 'N'}, {'value': 'xYx', 'id': 'O'}, {'value': 'gbz', 'id': 'P'},
    {'value': 'd4h', 'id': 'Q'}, {'value': '1Ow', 'id': 'R'}, {'value': 'Fw6', 'id': 'S'}, {'value': 'mor', 'id': 'T'},
    {'value': 'NDC', 'id': 'U'}, {'value': '7pm', 'id': 'V'}, {'value': 'Rn4', 'id': 'W'}, {'value': 'RVu', 'id': 'X'},
    {'value': 'dUW', 'id': 'Y'}, {'value': 'ic8', 'id': 'Z'}, {'value': 'aRm', 'id': '['}, {'value': 'po7', 'id': '\\'},
    {'value': 'tVA', 'id': ']'}, {'value': 'C5a', 'id': '^'}, {'value': 'G0m', 'id': '_'}, {'value': 'WHB', 'id': '`'},
    {'value': 'P91', 'id': 'a'}, {'value': 'cDf', 'id': 'b'}, {'value': '5Zp', 'id': 'c'}, {'value': 'pX5', 'id': 'd'},
    {'value': 'beG', 'id': 'e'}, {'value': 'sgd', 'id': 'f'}, {'value': '2Dl', 'id': 'g'}, {'value': 'YjH', 'id': 'h'},
    {'value': 'SQB', 'id': 'i'}, {'value': 'jJE', 'id': 'j'}, {'value': 'Gtw', 'id': 'k'}, {'value': 'JsK', 'id': 'l'},
    {'value': 'qfv', 'id': 'm'}, {'value': '5ty', 'id': 'n'}, {'value': 'BSm', 'id': 'o'}, {'value': 'Fbd', 'id': 'p'},
    {'value': 'xO7', 'id': 'q'}, {'value': 'W5R', 'id': 'r'}, {'value': 'ugh', 'id': 's'},{ 'value': 'nbs' , 'id': 't'},
	{'value': 'mgl', 'id': 'u'}, {'value': 'aqL', 'id': 'v'}, {'value': 'QJN', 'id': 'w'},{ 'value': 'X9d' , 'id': 'x'},
	{'value': 'lIB', 'id': 'y'}, {'value': 'Csm', 'id': 'z'}, {'value': 'uQ8', 'id': ''},{ 'value': 'EW7' , 'id': '|'},
	{'value': 'pP9', 'id': ''} , {'value': '5r3', 'id': '~'}, {'value': 'Nq0', 'id' :' '}]

# Hàm tạo kết nối SQL và trả về nó
def create_sql_connection():
    connection = mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="login",
    )
    return connection

# Hàm đóng kết nối SQL
def close_sql_connection(connection):
    connection.close()
    
# /**
# 	 * @description delete user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {user_delete  }
# 	 * @return data (payload, message)
# 	 */

@app.post("/delete")
async def deleteInformation(delete_data: delete):
    user_delete = delete_data.taikhoanxoa
    try:
        # Create connect to database
        # Tạo kết nối SQL
        connection = create_sql_connection()

        # create connection to sql 
        mycursor = connection.cursor()

        # Command INSERT in sql 
        Cmd_delete = ("DELETE FROM `login`.`user` WHERE `user` = %s")
        val_delete = (user_delete,)

        mycursor.execute(Cmd_delete, val_delete)

        # Commit 
        connection.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  


    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)
# /**
# 	 * @description show user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {  }
# 	 * @return data (payload, message)
# 	 */
@app.post("/show")
async def showInformation():
    try:
        # Create connection to database
        # Tạo kết nối SQL
        connection = create_sql_connection()

        # create connection to sql
        mycursor = connection.cursor()

        # Command INSERT
        Cmd_show = ("SELECT  `user` FROM `login`.`user`")

        mycursor.execute(Cmd_show)
        result = mycursor.fetchall()
        print("bảng show người dùng trong hệ thông :",result)
        # Commit 
        connection.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  


    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)
# /**
# 	 * @description registe user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {user_register,password_lv1_register }
# 	 * @return data (payload, message)
# 	 */
@app.post("/register")
def RegisterInformation(Register_data: Register):
    user_register = Register_data.taikhoannhap
    password_lv1_register = Register_data.matkhaunhap
    client_key = Fernet(fernet_key)
    fernet_key_lv2 = Fernet.generate_key()
    fernet_key_gui_sql = binascii.hexlify(fernet_key_lv2).decode()
    sever_key = Fernet(fernet_key_lv2)
    matkhauki_mahoa = sever_key.encrypt(password_lv1_register.encode())

    try:
        # Tạo kết nối SQL
        connection = create_sql_connection()
        mycursor = connection.cursor()

        # Command Select 
        Cmd_check_user = "SELECT * FROM `user` WHERE `user` = %s"
        val_check_user = (user_register,)
        mycursor.execute(Cmd_check_user, val_check_user)

        if mycursor.fetchone():
            print("User already exists. Please register another account.")
        else:
            Cmd_register = ("INSERT INTO `login`.`user`(`user`, `password`, `salt`) "
                            "VALUES (%s, %s, %s)")
            val_register = (user_register, matkhauki_mahoa, fernet_key_gui_sql)

            mycursor.execute(Cmd_register, val_register)
            connection.commit()
            print("Sign Up Success!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()

    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)
# /**
# 	 * @description update user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {user_update,password_lv1_update }
# 	 * @return data (payload, message)
# 	 */
@app.post("/update")
async def update_user(update_data: update):
    user_update = update_data.taikhoannhap
    password_lv1_update = update_data.matkhau_update
    password_lv1_old_hex = update_data.matkhau_old
    client_key = Fernet(fernet_key)
    # decode password_lv1_old
    password_old_lv1 = binascii.unhexlify(password_lv1_old_hex)
    create_key_old = Fernet(fernet_key)
    password_old = create_key_old.decrypt( password_old_lv1)
    # if passwword old client sent to sever the same as with password in sql effectuate 
    # Create key random 
    fernet_key_lv2 = Fernet.generate_key()
    fernet_key_gui_sql = binascii.hexlify(fernet_key_lv2).decode()
    sever_key = Fernet(fernet_key_lv2)

    matkhauki_mahoa = sever_key.encrypt(password_lv1_update.encode())
    print("The new password has been updated according to the key to download sql:", matkhauki_mahoa)
    try:
        # Create connecton to database 
        # Tạo kết nối SQL
        connection = create_sql_connection()
        # create connection to sql
        mycursor = connection.cursor()
        #
        Cmd_Login = ("SELECT  `user` ,`password`, `salt`  FROM `login`.`user` WHERE `user` = %s")
        val_login = (user_update,)

        mycursor.execute(Cmd_Login, val_login)
        result = mycursor.fetchall()
        if result:
            datarow = result[0]
            user_find = datarow[0]
            password_find_lv2 = datarow[1]
            print ("password taken from sql is :", password_find_lv2)
            keyfernet_find_hex = datarow[2]
         # Use the password from sql for the first decoded password
            keyfernet_find_sql = binascii.unhexlify(keyfernet_find_hex)
            create_key_sever = Fernet(keyfernet_find_sql)
            password_lv1_hex = create_key_sever.decrypt( password_find_lv2)
            password_lv1 = binascii.unhexlify(password_lv1_hex)
            client_key = Fernet(fernet_key)
            # After translating the password 2 times, compare it with the password the user entered
            password_sql = client_key.decrypt( password_lv1)
            print("mật khẩu cũ lấy lên từ sql và giãi mã ra là :", password_sql)


        # code compare password old with password sql the same as code login 
        if  password_sql == password_old :
                print("Confirm the old password matches and change the password successfully")
        # Command INSERT
                Cmd_update =  ("UPDATE `login`.`user` SET `password` = %s ,`salt` = %s WHERE `user` = %s")
                val_update = (matkhauki_mahoa,fernet_key_gui_sql, user_update)

                mycursor.execute(Cmd_update, val_update)
        else:
            print("Confirm old password does not match, change password failed ")
        # Commit 
        connection.commit()
        print("Record inserted successfully !")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  

    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)
        

# /**
# 	 * @description login user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {user_login,password_login }
# 	 * @return data (payload, message)
# 	 */
@app.post("/login")
async def LoginInformation(Login_data: Login):
    user_login = Login_data.taikhoannhap
    password_login = Login_data.matkhaunhap

    try:
        # Create connecttion to sql 
        # Tạo kết nối SQL
        connection = create_sql_connection()

        # # create connection to sql
        mycursor = connection.cursor()

        # Command SELECT
        Cmd_Login = ("SELECT  `user` ,`password`, `salt`  FROM `login`.`user` WHERE `user` = %s")
        val_login = (user_login,)

        mycursor.execute(Cmd_Login, val_login)
        result = mycursor.fetchall()
        if result:
            datarow = result[0]
            user_find = datarow[0]
            password_find_lv2 = datarow[1]
            print ("password taken from sql is :", password_find_lv2)
            keyfernet_find_hex = datarow[2]
            print("sql key fetched is ", keyfernet_find_hex)
            print("User information retrieved from sql is : ", user_find)
            
            # Use the password from sql for the first decoded password
            keyfernet_find_sql = binascii.unhexlify(keyfernet_find_hex)
            create_key_sever = Fernet(keyfernet_find_sql)
            password_lv1_hex = create_key_sever.decrypt( password_find_lv2)
            password_lv1 = binascii.unhexlify(password_lv1_hex)
            client_key = Fernet(fernet_key)
            # After translating the password 2 times, compare it with the password the user entered
            password_sql = client_key.decrypt( password_lv1)
            print("Password taken from translated sql", password_sql)
            

            # Decrypt the password taken from the client 
            password_nhan_client = binascii.unhexlify(password_login)
            # After translating the password 2 times, compare it with the password the user entered
            password_client = client_key.decrypt( password_nhan_client)
            print("The decrypted password is a value string taken from the client :" ,password_client )
            #Decode the string and print out the password
            def decrypt_combined_value(combined_value):
                decrypted_password = ''
                for i in range(0, len(combined_value), 3):  #Each 'value' value is 3 characters long
                    value_chunk = combined_value[i:i+3]
                    for item in tableCode:
                        if item['value'] == value_chunk:
                            decrypted_password += item['id']
                            break
                return decrypted_password
            decrypted_password = decrypt_combined_value(password_client)
            print(f"The root password the user enters is: {decrypted_password}")

            if  user_login == user_find and password_sql == password_client :
                print("Logged in successfully")
                timeout_minutes = 1
                timeout_seconds = timeout_minutes * 60
                start_time = time.time()  # Get the login start time

                while True:
                    elapsed_time = time.time() - start_time
                    remaining_time = timeout_seconds - elapsed_time

                    if remaining_time <= 0:
                        print("Login time has expired. Automatically log out.")
                        break

                    print(f"Time remaining: {int(remaining_time)} seconds", end="\r")
                    time.sleep(1)  # Wait 1 second before checking again
                else:
                    print("Login failed")
            else:
                print("Login failed")
        else:
            print("Account does not exist")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)
@app.post("/Read_Modbus_TCP")
def Read_Modbus_TCP(Read_data: Read_Modbus_TCP):
    ip          = Read_data.ip
    print("ip là ", ip)
    registers_0 = Read_data.registers_0
    registers_1 = Read_data.registers_1
    registers_2 = Read_data.registers_2
    registers_3 = Read_data.registers_3
    registers_4 = Read_data.registers_4
    date_timer  = Read_data.datetime
    try:
        # Create connection to database
        connection = create_sql_connection()

        # create connection to sql
        mycursor = connection.cursor()

        # Command INSERT
        Cmd_read = ("INSERT INTO `login`.`modbus`( `ip`,`thanhghi0`, `thanhghi1`, `thanhghi2`, `thanhghi3`, `thanhghi4`,`datetime`) "
                            "VALUES (%s ,%s, %s, %s, %s, %s, %s)")
        val_read = ( ip,registers_0, registers_1,registers_2,registers_3,registers_4,date_timer)

        mycursor.execute(Cmd_read, val_read)
        # Commit 
        connection.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  


    finally:
        # Close cursor and SQL connection
        mycursor.close()
        close_sql_connection(connection)




