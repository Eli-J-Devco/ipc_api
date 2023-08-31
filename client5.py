import requests
import json
import datetime

# Dữ liệu JSON bạn muốn gửi
data_to_send = {
    "SERIALNUMBER": "12345",
    "MODBUSPORT": "COM1",
    "MODBUSDEVICE": "Device1",
    "MODE": "Automatic",
    "PASSWORD": "password123"
}

# Chuyển dữ liệu thành JSON
json_data = json.dumps(data_to_send)

# Tạo tên tệp dựa trên thời gian
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"{current_time}.json"

# Ghi dữ liệu JSON vào tệp
with open(file_name, "w") as f:
    f.write(json_data)

# Địa chỉ URL của server
url = 'http://127.0.0.1:8000/receive_data/'

# Gửi dữ liệu và tệp lên server
files = {'file': open(file_name, 'rb')}
response = requests.post(url, files=files)

try:
    response_json = response.json()
    print(response_json)
except json.JSONDecodeError:
    print("Response is not a valid JSON")
try:
    response_json = response.json()
    print(response_json)
except Exception as e:
    print("Error decoding JSON:", e)
    
# Đảm bảo đóng tệp sau khi hoàn thành
files['file'].close()
