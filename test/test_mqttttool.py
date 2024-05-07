import asyncio
import logging
import os.path
import time
from pathlib import Path

import mqttools

from ..mqtt_service.core import MQTTSubscriber
from ..logger.logger import setup_logging
from ..src.publisher import Publisher

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
    client = MQTTSubscriber('localhost', 1883, subscriptions=['devices/create', 'devices/delete'])

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


asyncio.run(subscriber())
# asyncio.run(test_publish())
