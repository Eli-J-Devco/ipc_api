import asyncio
import base64
import enum
import json
import os.path
import pathlib
import time
import uuid

from mqtt_service.model import MessageModel, MetaData, Topic
from mqtt_service.mqtt import Publisher
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
                                "devices": [805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060]}
                       )

cre_msg = MessageModel(metadata=metadata,
                       topic=cre_topic,
                       message={"type": Action.CREATE.value,
                                "code": "CreateTCPDev",
                                "devices": [1061]}
                       )


async def publish(publisher: Publisher, msg: dict, topic: str):
    logger.info("Starting publisher")
    await publisher.start()
    logger.info("Publisher started")
    logger.info(f"Subscribing to topic: {topic}")
    await publisher.subscribe(f"{topic}")

    while True:
        logger.info(f"Publishing message: {msg}")
        publisher.send(f"{topic}", base64.b64encode(json.dumps(msg).encode("ascii")))
        logger.info("Message published")
        time.sleep(300)


if __name__ == "__main__":
    publisher = Publisher(
        host="localhost",
        port=1883,
        subscriptions=[Action.CREATE.value, Action.DELETE.value, Action.DEAD_LETTER.value],
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        will_qos=2
    )

    asyncio.run(publish(publisher, cre_msg.dict(), Action.CREATE.value))
