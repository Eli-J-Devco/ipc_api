import asyncio
import mqttools
import base64
import gzip
import json

class MQTTService:
    def __init__(self, host, port, username, password, serial_number):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.serial_number = serial_number
        self.message_queue = asyncio.Queue()  # Tạo hàng đợi cho tin nhắn
        self.topics = []
        self.received_messages = []  # Danh sách để lưu trữ tin nhắn

    def set_topics(self, *args):
        self.topics = [self.serial_number + topic for topic in args]

    def gzip_decompress(self, message):
        try:
            result_decode = base64.b64decode(message.decode('ascii'))
            result_decompress = gzip.decompress(result_decode)
            return json.loads(result_decompress)
        except Exception as err:
            print(f"Decompression error: '{err}'")
            return None 

    async def process_handle_messages(self, client):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                topic = message.topic
                payload = self.gzip_decompress(message.message)
                await self.message_queue.put((topic, payload))  # Đưa thông điệp vào hàng đợi
        except Exception as err:
            print(f"Error processing messages: '{err}'")

    async def handle_messages(self):
        while True:
            topic, message = await self.message_queue.get()  # Lấy tin nhắn từ hàng đợi
            self.received_messages.append((topic, message))  # Lưu tin nhắn vào danh sách
            # print(f"Received message on topic '{topic}': {message}")

    async def sud_data(self):
        try:
            client = mqttools.Client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=bytes(self.password, 'utf-8'),
                subscriptions=self.topics,
                connect_delays=[1, 2, 4, 8]
            )
            await client.start()

            # Chạy đồng thời các hàm xử lý
            await asyncio.gather(
                self.process_handle_messages(client),
                self.handle_messages()
            )

        except Exception as err:
            print(f"Error in sud_data: '{err}'")
        finally:
            await client.stop()

# Hàm main để chạy dịch vụ
async def main():
    mqtt_service = MQTTService(
        host='115.78.133.129', 
        port=1883, 
        username='nextwave', 
        password='123654789', 
        serial_number='G83VZT33'
    )
    mqtt_service.set_topics('/Devices/All', '/CPU/Information')  # Thay đổi theo nhu cầu của bạn
    await mqtt_service.sud_data()
    
    for topic, message in mqtt_service.received_messages:
        print(f"Topic: {topic}")
        print(f"Message: {message}")


# Chạy hàm main
if __name__ == "__main__":
    asyncio.run(main())
