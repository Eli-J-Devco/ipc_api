import asyncio
import base64
import enum
import json
import logging
import os.path
import pathlib
import time
import uuid

from ..mqtt_service.model import MessageModel, MetaData, Topic
from ..mqtt_service.core import MQTTPublisher
from ..src.publisher import Publisher
from ..logger.logger import setup_logging

logger = setup_logging(file_name="send_creation_devices",
                       log_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "log"))


class DeviceState(enum.Enum):
    CREATING = 1
    CREATED = 2
    DELETING = 3
    DELETED = 4


class Action(enum.Enum):
    CREATE = "devices/create"
    DELETE = "devices/delete"
    DEAD_LETTER = "devices/dead-letter"


metadata = MetaData(retry=3)
del_topic = Topic(target=Action.DELETE.value, failed=Action.DEAD_LETTER.value)
cre_topic = Topic(target=Action.CREATE.value, failed=Action.DEAD_LETTER.value)

del_msg = MessageModel(metadata=metadata,
                       topic=del_topic,
                       message={"type": Action.DELETE.value,
                                "devices": [700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714,
                                            715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729,
                                            730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744,
                                            745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759,
                                            760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774,
                                            775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789,
                                            790, 791, 792, 793, 794, 795, 796, 797, 798, 799]}
                       )

cre_msg = MessageModel(metadata=metadata,
                       topic=cre_topic,
                       message={"type": Action.CREATE.value,
                                "devices": [635, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681,
                                            682,
                                            683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697,
                                            698,
                                            699]}
                       )


async def publish(publisher: MQTTPublisher, msg: dict):
    logger.info("Starting publisher")
    await publisher.start()
    logger.info("Publisher started")
    logger.info(f"Subscribing to topic: {Action.CREATE.value}")
    await publisher.subscribe(f"{Action.CREATE.value}")

    while True:
        logger.info(f"Publishing message: {msg}")
        publisher.send(f"{Action.CREATE.value}", base64.b64encode(json.dumps(msg).encode("ascii")))
        logger.info("Message published")
        time.sleep(300)


if __name__ == "__main__":
    publisher = Publisher(
        host="localhost",
        port=1883,
        topic=[f"{Action.CREATE.value}"],
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2
    )

    asyncio.run(publish(publisher.client, del_msg.dict()))
