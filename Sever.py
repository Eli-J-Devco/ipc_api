# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

# Tạo một lớp Pydantic để đại diện cho dữ liệu đăng nhập từ client
class LoginData(BaseModel):
    username: str
    password: str
# Danh sách người dùng hợp lệ (đây là ví dụ, bạn nên sử dụng cơ sở dữ liệu thực tế)
valid_users = {
    "user1": "password1",
    "user2": "password2",
}
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
    if username in valid_users and valid_users[username] == password:
        return {"message": "Đăng nhập thành công"}
    else:
        return {"message": "Đăng nhập thất bại"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
