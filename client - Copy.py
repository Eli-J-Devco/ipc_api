import httpx
import json
import asyncio

url = "http://127.0.0.1:8000/receive_data/"  # Địa chỉ của server FastAPI

data_to_send = {"key": "value"}  # Dữ liệu bạn muốn gửi

async def send_data():
    while True:
        try:
            response = httpx.post(url, json=data_to_send)

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




