import asyncio
import logging
import os.path
import time
from pathlib import Path

import mqttools

from mqtt_service.mqtt import Subscriber, Publisher
from ..logger.logger import setup_logging

# logging.basicConfig(level=logging.INFO)

logger = setup_logging(log_path=os.path.join(Path(__file__).parent.absolute(), "log"))


async def test_publish():
    publisher = Publisher(
        host="localhost",
        port=1883,
        topic=[f"devices/create"],
        client_id="publisher-creating-1",
        qos=2
    )

    await publisher.connect()

    while True:
        try:
            publisher.publish(b"test message")
            time.sleep(300)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error publishing message: {e}")
    await publisher.disconnect()


async def subscriber():
    client = Subscriber('localhost', 1883, subscriptions=['devices/create', 'devices/delete'])

    await client.start()

    logger.info('Waiting for messages.')

    while True:
        topic, message, retain, response_topic = await client.messages.get()

        if topic is None:
            logger.info('Broker connection lost!')
            break

        logger.info(f'Topic:         {topic}')
        logger.info(f'Message:       {message}')
        logger.info(f'Retain:        {retain}')
        logger.info(f'ResponseTopic: {response_topic}')


async def handle_messages(client):
    while True:
        message = await client.messages.get()

        if message is None:
            print('Connection lost.')
            break

        print(f'Got {message.message} on {message.topic}.')


class Test(mqttools.Client):
    async def on_message(self, message):
        await self._messages.put(message)


class MQTTSubscriber(Subscriber):
    async def get_message(self):
        while True:
            message = await self.messages.get()

            if message is None:
                print('Connection lost.')
                break

            print(f'Got {message.message} on {message.topic}.')


async def reconnector():
    client = Publisher('115.78.133.129',
                       1883,
                       username='nextwave',
                       password=bytes('123654789', 'utf-8'),
                       client_id='subscriber-1',
                       subscriptions=['devices/create', 'devices/delete'],
                       connect_delays=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], )

    await client.start()
    client.send('G83VZT33/Init/API/Requests', '{"CODE": "DeleteDev", '
                                              '"PAYLOAD": {"device": '
                                              '[{"id": 804, "name": "string", "connect_type": "Modbus/TCP", "id_communication": 3, "mode": 0}],'
                                              'delete_mode: 2}}')


asyncio.run(reconnector())
# asyncio.run(subscriber())
# asyncio.run(test_publish())
