# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

import requests
import bcrypt

# Thay đổi URL thành URL thực tế của server
server_url = "http://127.0.0.1:8000/login"

# Giá trị input bạn muốn gửi lên server
username = input("nhập vào tài khoản:")
password = input("nhập vào mật khẩu :")

# Mã hóa mật khẩu
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode(), salt)

# Tạo một dictionary chứa giá trị input
payload = {"usernameclient": username, "password": hashed_password}

# Gửi yêu cầu POST đến server FastAPI với dữ liệu JSON
response = requests.post(server_url, json=payload)

# Giải mã dữ liệu trả về từ server
data = response.json()
print(data)
