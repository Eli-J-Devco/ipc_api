import requests
import json
import time

url = 'http://127.0.0.1:8000/receive_data/'  # Đảm bảo rằng máy chủ FastAPI đang chạy

data_to_send = {
    "SERIALNUMBER": "12345",
    "MODBUSPORT": "COM1",
    "MODBUSDEVICE": "Device1",
    "MODE": "Automatic",
    "PASSWORD": "password123"
}

json_data = json.dumps(data_to_send)
headers = {'Content-Type': 'application/json'}

while True:
    response = requests.post(url, data=json_data, headers=headers)
    
    if response.status_code == 200:
        print("Yêu cầu thành công!")
    else:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)
    
    time.sleep(5)  # Chờ 5 giây trước khi gửi lại
    