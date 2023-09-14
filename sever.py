from fastapi import FastAPI ,Request
from pydantic import BaseModel
import mysql.connector
import bcrypt
from cryptography.fernet import Fernet
import binascii
import threading
import time

app = FastAPI()

# Tạo 1 lớp để nhận dữ liệu từ client đăng nhập
class Login(BaseModel):
    taikhoannhap: str
    matkhaunhap: str

# Tạo 1 lớp để nhận dữ liệu từ client đăng kí
class Register(BaseModel):
    taikhoannhap: str
    matkhaunhap: str

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


@app.post("/register")
async def RegisterInformation(Register_data: Register):
    user_register = Register_data.taikhoannhap
    password_lv1_register = Register_data.matkhaunhap
    # password_decode_hex = binascii.unhexlify(password_lv1_register)
    # print("mật khẩu nhận đã mã hóa hex  ", password_decode_hex)
    #mật khẩu cố định cho cho Fernet
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)
    # password_goc = client_key.decrypt( password_decode_hex)
    # print("mật khẩu người dùng nhập vào là " , password_goc)
    

    # Tạo một khóa Fernet ngẫu nhiên
    fernet_key_lv2 = Fernet.generate_key()
    fernet_key_gui_sql = binascii.hexlify(fernet_key_lv2).decode()
    sever_key = Fernet(fernet_key_lv2)

    # Mã hóa mật khẩu bcrypt với khóa Fernet lần 2 lấy tiếp nội dung từ client gửi qua dưới dạng hex 
    matkhauki_mahoa = sever_key.encrypt(password_lv1_register.encode())

    try:
        # Tạo kết nối đến database
        connection = mysql.connector.connect(
            user="root",
            password="123456",
            host="localhost",
            database="login",
        )

        # Tạo con trỏ trong MySQL
        mycursor = connection.cursor()

        # Câu truy vấn INSERT
        Cmd_register = ("INSERT INTO `login`.`user`(`user`, `password`, `salt`) "
                        "VALUES (%s, %s, %s)")
        val_register = (user_register, matkhauki_mahoa,fernet_key_gui_sql)

        mycursor.execute(Cmd_register, val_register)

        # Commit giao dịch
        connection.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  # Lưu ý: Rollback giao dịch nếu có lỗi

    finally:
        mycursor.close()
        connection.close()

@app.post("/login")
async def LoginInformation(Login_data: Login):
    user_login = Login_data.taikhoannhap
    password_login = Login_data.matkhaunhap

    try:
        # Tạo kết nối đến database
        connection = mysql.connector.connect(
            user="root",
            password="123456",
            host="localhost",
            database="login",
        )

        # Tạo con trỏ trong MySQL
        mycursor = connection.cursor()

        # Câu truy vấn SELECT
        Cmd_Login = ("SELECT  `user` ,`password`, `salt`  FROM `login`.`user` WHERE `user` = %s")
        val_login = (user_login,)

        mycursor.execute(Cmd_Login, val_login)
        result = mycursor.fetchall()
        if result:
            datarow = result[0]
            user_find = datarow[0]
            password_find_lv2 = datarow[1]
            keyfernet_find_hex = datarow[2]
            print("key sql lấy lên là ", keyfernet_find_hex)
            print("thông tin người dùng lấy lên từ sql là : ", user_find)
            
            # dùng mật khẩu từ sql để dịch lần 1
            keyfernet_find_sql = binascii.unhexlify(keyfernet_find_hex)
            create_key_sever = Fernet(keyfernet_find_sql)
            password_lv1_hex = create_key_sever.decrypt( password_find_lv2)
            password_lv1 = binascii.unhexlify(password_lv1_hex)
            # dùng mật khẩu cố định giống bên client để dịch lần 2
            fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
            client_key = Fernet(fernet_key)
            # mật khẩu sau khi dịch 2 lần lấy này so sánh với mật khẩu người dùng nhập qua
            password_sql = client_key.decrypt( password_lv1)
            print("mật khẩu lấy từ sql đã dịch ra", password_sql)
            

            # Giải mã mật khẩu lấy từ client  
            password_nhan_client = binascii.unhexlify(password_login)
            # mật khẩu sau khi dịch 2 lần lấy này so sánh với mật khẩu người dùng nhập qua
            password_client = client_key.decrypt( password_nhan_client)
            print("mật khẩu giãi mã dạng chuỗi value lấy từ client :" ,password_client )
            # Giải mã chuỗi và in ra mật khẩu
            def decrypt_combined_value(combined_value):
                decrypted_password = ''
                for i in range(0, len(combined_value), 3):  # Mỗi giá trị 'value' có độ dài 3 ký tự
                    value_chunk = combined_value[i:i+3]
                    for item in tableCode:
                        if item['value'] == value_chunk:
                            decrypted_password += item['id']
                            break
                return decrypted_password
            decrypted_password = decrypt_combined_value(password_client)
            print(f"Mật khẩu gốc người dùng nhập là : {decrypted_password}")

            if  user_login == user_find and password_sql == password_client :
                print("Đăng nhập thành công")
                timeout_minutes = 1
                timeout_seconds = timeout_minutes * 60
                start_time = time.time()  # Lấy thời gian bắt đầu đăng nhập

                while True:
                    elapsed_time = time.time() - start_time
                    remaining_time = timeout_seconds - elapsed_time

                    if remaining_time <= 0:
                        print("Thời gian đăng nhập đã hết. Tự động thoát ra ngoài.")
                        break

                    print(f"Thời gian còn lại: {int(remaining_time)} giây", end="\r")
                    time.sleep(1)  # Đợi 1 giây trước khi kiểm tra lại
                else:
                    print("Đăng nhập thất bại")
            else:
                print("Đăng nhập thất bại")
        else:
            print("Tài khoản không tồn tại")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        mycursor.close()
        connection.close()




