# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Tạo một lớp Pydantic để đại diện cho dữ liệu đăng nhập từ client
class LoginData(BaseModel):
    username: str
    password: str
# Tạo kết nối đến database
connection = mysql.connector.connect(
    user="root",
    password="123456",
    host="localhost",
    database="login",
)

# Lấy tất cả dữ liệu từ bảng data
cursor = connection.cursor()
cursor.execute("SELECT * FROM data")
# Duyệt qua các hàng dữ liệu
for row in cursor:
    db_id = row[0]
    db_username = row[1]
    db_password = row[2]
    print(db_id)
    print(db_username)
    print(db_password)
# /**
# 	 * @description Login
# 	 * @author binhnguyen
# 	 * @since 09-07-2023
# 	 * @param {}
# 	 * @return data (status, message)
# 	 */
@app.post("/login")
async def login(data: LoginData):
    username = data.username
    password = data.password


    # Kiểm tra thông tin đăng nhập với danh sách người dùng hợp lệ
    if db_id == 1 and db_username == "user1" and db_password == "password1":
        return {"message": "Đăng nhập thành công"}
    else:
        return {"message": "Đăng nhập thất bại"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
