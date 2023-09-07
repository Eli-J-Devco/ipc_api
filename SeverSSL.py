from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import bcrypt

app = FastAPI()

# Tạo một lớp Pydantic để đại diện cho dữ liệu đăng nhập từ client
class LoginData(BaseModel):
    usernameclient: str
    password: str

# Tạo kết nối đến database
connection = mysql.connector.connect(
    user="root",
    password="123456",
    host="localhost",
    database="login",
)

# /**
#      * @description Login
#      * @author binhnguyen
#      * @since 09-07-2023
#      * @param {}
#      * @return data (status, message)
#      */
@app.post("/login")
async def login(data: LoginData):
    username = data.usernameclient
    password = data.password
    print(f"Received input from client: {username, password}")

    # Lấy tất cả dữ liệu từ bảng data
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM data where id=1")

    # Duyệt qua các hàng dữ liệu
    for row in cursor:
        db_id = row[0]
        db_username = row[1]
        db_password_hashed = row[2]

    # Kiểm tra thông tin đăng nhập với danh sách người dùng hợp lệ
    if db_id == 1 and db_username == username:
        # So sánh mật khẩu đã mã hóa
        if bcrypt.checkpw(password.encode(), db_password_hashed.encode()):
            return {"message": "Đăng nhập thành công"}
    
    return {"message": "Đăng nhập thất bại"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
