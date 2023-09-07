# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 

import requests

inputtk=input("nhập vào tài khoản :")
inputmk=input("nhập vào mật khẩu : ")

# Địa chỉ URL của API server
url = "http://127.0.0.1:8000/login"

# Tạo một yêu cầu POST để đăng nhập
data = {"username": inputtk, "password": inputmk}
response = requests.post(f"{url}/login", json=data)

# # Xem xét phản hồi từ API server
if response.status_code == 200:
    response_json = response.json()
    if "message" in response_json and response_json["message"] == "Đăng nhập thành công":
        print("Đăng nhập thành công")
        # Ở đây, bạn có thể xử lý token hoặc thông tin khác từ phản hồi
    else:
        print("Đăng nhập thất bại")
else:
    print("Lỗi khi gửi yêu cầu đến server")