# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

from fastapi import FastAPI
from pydantic import BaseModel
import mysql
app = FastAPI()

# Thông tin cơ sở dữ liệu MySQL
db_config = {
    'host': 'your_mysql_host',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'your_database_name',
}

# Model để đọc thông tin đăng nhập từ client
class UserLogin(BaseModel):
    username: str
    password: str
# /**
# 	 * @description Login
# 	 * @author binhnguyen
# 	 * @since 09-07-2023
# 	 * @param {}
# 	 * @return data (status, message)
# 	 */
@app.post("/login")
async def login(user_login: UserLogin):
    # Kết nối đến cơ sở dữ liệu MySQL
    try:
        connection = mysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # Thực hiện truy vấn SQL để kiểm tra thông tin đăng nhập
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (user_login.username, user_login.password))
            result = cursor.fetchone()
            
            if result:
                return {"message": "Đăng nhập thành công!"}
            else:
                return {"message": "Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập."}
    except Exception as e:
        return {"message": f"Lỗi trong quá trình xử lý yêu cầu: {str(e)}"}
    finally:
        connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
