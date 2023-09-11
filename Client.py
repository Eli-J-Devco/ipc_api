# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

import requests
import binascii
import bcrypt
from cryptography.fernet import Fernet
import mysql.connector

 # Thay đổi URL thành URL thực tế của server
server_url = "http://127.0.0.1:8000/login"
# Giá trị input bạn muốn gửi lên server
input_user= input("Nhập giá trị muốn gửi:")
input_passwword = input("Nhập giá trị muốn gửi:")

# kết nối với sql 
connection = mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="login",
    )
    # Lấy tất cả dữ liệu từ bảng data
cursor = connection.cursor()
commadsql = ("SELECT salt FROM login.data WHERE user = %s")
val = (input_user,)
cursor.execute(commadsql, val)
result = cursor.fetchall()
if result:
    tuplesalt = result[0]
    salt_hex = tuplesalt[0]
    print("mã salt hex lấy lên từ sql là :",salt_hex)
    saltfull = binascii.unhexlify(salt_hex)
    print("salt lấy lên từ sql: ", saltfull)
else:
    print("Không tìm thấy thông tin người dùng.")
# mỗi lần tạo salt thì mật khẩu sẽ khác nhau nên muốn cùng salt thì phải gửi lun mã salt này vào sql 
password_lv1 = bcrypt.hashpw(input_passwword.encode(), saltfull)
print(" Mật khẩu băm qua bcrypt", password_lv1)

# Tạo một khóa ngẫu nhiên cho Fernet
fernet_key = Fernet.generate_key()
client_key = Fernet(fernet_key)
print("đây là ramdom key :",client_key)
# Mã hóa mật khẩu bcrypt với khóa Fernet
password_lv2 = client_key.encrypt(password_lv1)

print( "Mật khẩu băm qua fernet :" , password_lv2)

# Chuyển đổi dữ liệu bytes thành chuỗi hex
password_lv2_hex = binascii.hexlify(password_lv2).decode()
print("Mã đã chuyển qua hex ",password_lv2_hex)

# Chuyển đổi dữ liệu key bcrypt thành key hex để gửi đi 
client_key_hex = binascii.hexlify(fernet_key).decode()
print("Key đã chuyển qua hex ",client_key_hex)

# Tạo một dictionary chứa giá trị input // payload này tên như thế nào thì class InformationUser(BaseModel):/client_user: str/client_password: str tên như thế mới kết nối được 
payload = {"client_user": input_user,"client_password": password_lv2_hex,"client_key":client_key_hex}
#client_key_hex => mã hóa lại byte => client_key = Fernet(fernet_key) để lấy key thật 

# Gửi yêu cầu POST đến server FastAPI với dữ liệu JSON
response = requests.post(server_url, json=payload)
# Kiểm tra phản hồi từ server
# if response.status_code == 200:
#     print("Đăng nhập thành công!")
# else:
#     print("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.")
