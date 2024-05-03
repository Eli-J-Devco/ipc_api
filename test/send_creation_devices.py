import base64
import enum
import json
import logging
import time
import uuid

from ..src.publisher import Publisher
from ..logger.logger import setup_logging

setup_logging()


class DeviceState(enum.Enum):
    CREATING = 1
    CREATED = 2
    DELETING = 3
    DELETED = 4


class Action(enum.Enum):
    CREATE = "devices/create"
    DELETE = "devices/delete"


msg = {
    "metadata": {
        "retry": 3
    },
    "type": Action.CREATE.value,
    "devices": [571, 572]
}


if __name__ == "__main__":
    publisher = Publisher(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.CREATE.value}",
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2
    )
    publisher.connect()

    while True:
        publisher.publish(base64.b64encode(json.dumps(msg).encode("ascii")))
        time.sleep(300)

