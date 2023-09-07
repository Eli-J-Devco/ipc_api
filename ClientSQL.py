# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 
import requests

# URL của server
server_url = "http://127.0.0.1:8000/login"  # Thay đổi thành URL thực tế của server

# Thông tin đăng nhập của người dùng
username = input("Nhập vào tên người dùng :")
password = input("Nhập vào mật khẩu người dùng :")

# Tạo dữ liệu yêu cầu (thông tin đăng nhập)
data = {
    "username": username,
    "password": password
}

# Gửi yêu cầu POST đến server
response = requests.post(server_url, data=data)

# Kiểm tra phản hồi từ server
if response.status_code == 200:
    print("Đăng nhập thành công!")
    # Xử lý phản hồi từ server nếu cần
else:
    print("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.")
