import enum
import uuid

from ..src.publisher import Publisher
from ..src.subscriber import Subscriber
from ..logger.logger import setup_logging

setup_logging()


class DeviceState(enum.Enum):
    CREATING = 1
    CREATED = 2
    DELETING = 3
    DELETED = 4
    DEAD_LETTER = 5


class Action(enum.Enum):
    CREATE = "devices/create"
    DELETE = "devices/delete"
    DEAD_LETTER = "devices/dead-letter"


if __name__ == "__main__":
    re_publisher = Publisher(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.CREATE.value}",
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2
    )

    dead_letter_publisher = Publisher(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.DEAD_LETTER.value}",
        client_id=f"publisher-{DeviceState.DEAD_LETTER.name.lower()}-{uuid.uuid4()}",
        qos=2
    )
    subscriber = Subscriber(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.CREATE.value}",
        client_id=f"sub-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2,
        retry_publisher=re_publisher,
        dead_letter_publisher=dead_letter_publisher
    )

    subscriber.connect()
    subscriber.subscribe()
