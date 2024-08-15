# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import gzip
import base64
import mqttools
import paho.mqtt.publish as publish
# ----- MQTT -----
class MQTTService:
    def __init__(self, host, port, username, password, serial_number):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.serial_number = serial_number
        self.topics = []

    def set_topics(self, *args):
        self.topics = [self.serial_number + topic for topic in args]
    def stop(self):
        self.running = False  # Đặt cờ dừng
    async def process_handle_messages(self, client):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                topic = message.topic
                payload = self.gzip_decompress(message.message)
                # Gọi hàm processMessage
                return topic, payload
        except Exception as err:
            print(f"Error processing messages: '{err}'")

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
            while True:
                await client.start()
                topic , message = await self.process_handle_messages(client)
                if topic and message: 
                    return topic, message
        except Exception as err:
            print(f"Error MQTT processSudAllMessageFromMQTT: '{err}'")
        finally:
            await client.stop()
    def gzip_decompress(self, message):
        try:
            result_decode = base64.b64decode(message.decode('ascii'))
            result_decompress = gzip.decompress(result_decode)
            return json.loads(result_decompress)
        except Exception as err:
            print(f"Decompression error: '{err}'")
            return None  # Trả về None nếu có lỗi
    # Phương thức push_data
    def push_data(self, topic, data_send):
        try:
            payload = json.dumps(data_send)
            full_topic = self.serial_number + topic  # Thêm serial_number vào topic
            publish.single(full_topic, payload, hostname=self.host,
                            port=self.port,
                            auth={'username': f'{self.username}', 
                                    'password': f'{self.password}'})
        except Exception as err:
            print(f"Error MQTT public: '{err}'")
            pass

    # Phương thức publish_zip
    def push_data_zip(self, topic, message):
        try:
            gzip_compress = gzip.compress(json.dumps(message).encode("ascii"), 9)
            payload = base64.b64encode(gzip_compress)
            full_topic = self.serial_number + topic  # Thêm serial_number vào topic
            publish.single(full_topic, payload=payload, hostname=self.host,
                            retain=False, port=self.port,
                            auth={'username': f'{self.username}', 
                                    'password': f'{self.password}'})
        except Exception as err:
            print(f"Error MQTT public: '{err}'")

def push_data_to_mqtt(host,port,topic,username, password, data_send):
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                    port=port,
                    auth = {'username':f'{username}', 
                            'password':f'{password}'})
        # publish.single(Topic, payload, hostname=Broker,
        #             retain=False, port=Port)
    # except Error as err:
    #     print(f"Error MQTT public: '{err}'")
    except Exception as err:
    # except:
        
        print(f"Error MQTT public: '{err}'")
        pass