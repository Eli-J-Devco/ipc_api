# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import bcrypt
from cryptography.fernet import Fernet
import binascii

app = FastAPI()

# Định nghĩa một model Pydantic để kiểm tra dữ liệu đầu vào từ client
class InformationUser(BaseModel):
    client_user: str
    client_password: str
    client_key : str

# /**
# * @description Login
# 	 * @author binhnguyen
# 	 * @since 09-07-2023
# 	 * @param {}
# 	 * @return data (status, data, message)
# 	 */
@app.post("/login")
async def receive_input(client_data: InformationUser):
    sever_user = client_data.client_user
    sever_password_hex = client_data.client_password
    sever_key_hex =client_data.client_key
    # In thông tin nhận được ra màn hình console
    print(f"Received user from client: {sever_user}")
    print(f"Received password from client: {sever_password_hex}")
    # chuyển từ mã hex sang pass lv2 
    password_lv2 = binascii.unhexlify(sever_password_hex)
    print("mật khẩu đã chuyển lại qua byte :", password_lv2)
    # chuyển từ mã hex key sang byte
    sever_key = binascii.unhexlify(sever_key_hex)
    print("key đã chuyển lại qua byte :", sever_key)
    # này mới là mã tạo key chưa phải là key mình phải chuyển lại key 
    key = Fernet(sever_key)
    # decoded_password_lv2 = cipher_suite.decrypt(password_lv2 , sever_key)
    decoded_password_lv2 = key.decrypt(password_lv2)
    print("đây là mật khẩu đã giải mã lv2 còn lv1  :", decoded_password_lv2)
    # bắt đầu truy vấn sql để lấy thông tin sql lên so sánh 
    # Tạo kết nối đến database
    connection = mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="login",
    )
    # Lấy tất cả dữ liệu từ bảng data
    cursor = connection.cursor()
    commadsql = ("SELECT user, password FROM login.data WHERE user = %s")
    val = (sever_user,)
    cursor.execute(commadsql, val)
    result = cursor.fetchall()
    datarow=result[0]
    user_find =datarow[0]
    password_find_hex=datarow[1]
    print("mật khẩu đọc lên là hex phải bằng với ghi xuống trong fil đăng nhập", password_find_hex)
    password_find = binascii.unhexlify(password_find_hex)
    print("key đã chuyển lại qua byte :", sever_key)
    # 2 mật khẩu lấy được rồi nhưng còn mã hóa bcrypt 
    print("đây là mật khẩu đã giải mã lv2 còn lv1  :", decoded_password_lv2)
    print("mật khẩu lấy lên từ sql và đã mã hóa lại thành mật khẩu khi ghi xuống : " , password_find)
    chuoi1 = str(decoded_password_lv2)
    chuoi2 = str(password_find)
    # Kiểm tra thông tin đăng nhập với danh sách người dùng hợp lệ
    if sever_user == user_find :
        print("người dùng trùng khớp")
        # So sánh mật khẩu đã mã hóa
        if chuoi1== chuoi2:
            print("đăng nhập thành công")
        return {"message": "Đăng nhập thành công"}
    else:
        print("đăng nhập thất bại : ")
        return {"message": "Đăng nhập thất bại"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
