import httpx
import asyncio
import json

url = "http://127.0.0.1:8000/receive_data/"  # Địa chỉ của server FastAPI

async def send_data():
    try:
        while True:
            data_to_send = {
                "SERIALNUMBER": "12345",
                "MODBUSPORT": "502",
                "MODBUSDEVICE": "1",
                "MODE": "auto",
                "PASSWORD": "securepassword"
            }

            headers = {"Content-Type": "application/json"}  # Đặt header cho request

            json_data = json.dumps(data_to_send)  # Định dạng dữ liệu thành JSON

            response = await httpx.post(url, data=json_data, headers=headers)
            print(response)
            if response.status_code == 200:
                response_data = response.json()
                print(response_data['message'])
            else:
                print("Error sending data")

            await asyncio.sleep(5)  # Chờ 5 giây trước khi gửi lần tiếp theo
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_data())
