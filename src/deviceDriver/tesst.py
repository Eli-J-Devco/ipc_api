import asyncio
import mqttools
import base64
import json
import gzip

async def main():
    host = "115.78.133.129"
    port = 1883
    username = "nextwave"
    password = "123654789"
    serial_number_project = "G83VZT33"
    topic1 = "/Control/Write"

    await sub_mqtt(host, port, username, password, serial_number_project, topic1)

async def sub_mqtt(host, port, username, password, serial_number_project, topic1):
    topics = [topic1]
    try:
        client = mqttools.Client(
            host=host,
            port=port,
            username=username,
            password=bytes(password, 'utf-8'),
            subscriptions=topics,
            connect_delays=[1, 2, 4, 8]
        )

        while True:
            await client.start()
            await handle_messages_driver(client, host, port, username, password)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT sub_mqtt: '{err}'")

async def handle_messages_driver(client, host, port, username, password):
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = gzip_decompress(message.message)
            await process_message(topic, payload, host, port, username, password)
    except Exception as err:
        print(f"Error handle_messages_driver: '{err}'")

def gzip_decompress(message):
    try:
        result_decode = base64.b64decode(message.decode('ascii'))
        result_decompress = gzip.decompress(result_decode)
        return json.loads(result_decompress)
    except Exception as err:
        print(f"decompress: '{err}'")

async def process_message(topic, payload, host, port, username, password):
    # Implement your message processing logic here
    print(f"Received message on topic: {topic}")
    print(f"Payload: {payload}")

if __name__ == "__main__":
    asyncio.run(main())
