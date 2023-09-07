# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

import requests

 # Thay đổi URL thành URL thực tế của server
server_url = "http://127.0.0.1:8000/login"
# Giá trị input bạn muốn gửi lên server
input_value1= str(input("Nhập giá trị muốn gửi:"))
input_value2 = str(input("Nhập giá trị muốn gửi:"))

# Tạo một dictionary chứa giá trị input
payload = {"input_value1": input_value1,"input_value2": input_value2,}

# Gửi yêu cầu POST đến server FastAPI với dữ liệu JSON
response = requests.post(server_url, json=payload)
# Kiểm tra phản hồi từ server
# if response.status_code == 200:
#     print("Đăng nhập thành công!")
# else:
#     print("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.")
