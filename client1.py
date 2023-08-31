import httpx
import json
import asyncio

url = "http://127.0.0.1:8000/receive_data/"  # Địa chỉ của server FastAPI

def generate_data(value):
    return {"key": value}

async def send_data():
    while True:
        try:
            for i in range(1, 6):  # Thay đổi giá trị từ 1 đến 5
                data_to_send = generate_data(i)
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