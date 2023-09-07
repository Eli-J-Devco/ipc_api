# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import bcrypt
app = FastAPI()

# Định nghĩa một model Pydantic để kiểm tra dữ liệu đầu vào từ client
class InputData(BaseModel):
    input_value1: str
    input_value2: str

# /**
# 	 * @description Login
# 	 * @author binhnguyen
# 	 * @since 09-07-2023
# 	 * @param {}
# 	 * @return data (status, message)
# 	 */
@app.post("/login")
async def receive_input(input_data: InputData):
    received_input1 = input_data.input_value1
    received_input2 = input_data.input_value2
    # In thông tin nhận được ra màn hình console
    print(f"Received input from client: {received_input1}")
    print(f"Received input from client: {received_input2}")
    # Thực hiện xử lý dữ liệu tại đây (ví dụ: lưu vào cơ sở dữ liệu, xử lý, v.v.)


    # Tạo kết nối đến database
    connection = mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="login",
    )

    # Lấy tất cả dữ liệu từ bảng data
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM login.data where id = 13")
    
    # Duyệt qua các hàng dữ liệu
    for row in cursor:
        db_username = row[1]
        db_password_hashed = row[2]
    # Kiểm tra thông tin đăng nhập với danh sách người dùng hợp lệ
    if db_username == received_input1:
        # So sánh mật khẩu đã mã hóa
        if bcrypt.checkpw(received_input2.encode('utf-8'), db_password_hashed.encode('utf-8')):
            # a=print(db_username)
            # b=print(db_password_hashed)
            print("đăng nhập thành công")
        return {"message": "Đăng nhập thành công"}
    else:
        print("đăng nhập thất bại : ")
        return {"message": "Đăng nhập thất bại"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
