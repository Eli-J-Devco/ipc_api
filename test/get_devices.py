import logging
import pathlib
from functools import reduce
import requests

from ..src.create_devices_model import DeviceModel
from ..logger.logger import setup_logging
from ..src.utils.password_hasher import AccountHasher
from ..src.config import config

setup_logging(log_path=f"{pathlib.Path(__file__).parent.absolute()}\\log")


def create_table(devices: list[int]):
    try:
        username = config.SETUP_USERNAME
        password = config.SETUP_PASSWORD

        username = AccountHasher().encrypt(username.encode(), config.PASSWORD_SECRET_KEY.encode())
        password = AccountHasher().encrypt(password.encode(), config.PASSWORD_SECRET_KEY.encode())

        logging.info(f"Username: {username}")
        logging.info(f"Password: {password}")

        response = requests.post(config.SETUP_URL + config.SETUP_AUTH_ENDPOINT,
                                 data={
                                     "username": username,
                                     "password": password
                                 },
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

        token = response.json().get("access_token")
        logging.info(f"Token: {token}")

        response = requests.post(config.SETUP_URL + config.SETUP_DEVICES_ENDPOINT,
                                 headers={"Authorization": f"Bearer {token}"})

        all_devices = response.json()
        devices_info = []
        id_templates = {}
        for device in all_devices:
            if device.get("id") in devices:
                adding_device = DeviceModel(**device)
                if adding_device.id_template not in id_templates:
                    id_templates[adding_device.id_template] = (requests
                                                               .post(config.SETUP_URL +
                                                                     config.SETUP_POINTS_ENDPOINT +
                                                                     f"?id_template={adding_device.id_template}",
                                                                     headers={
                                                                         "Authorization": f"Bearer {token}"
                                                                     })
                                                               .json())
                adding_device.points = id_templates[adding_device.id_template]
                devices_info.append(adding_device)
        logging.info(f"Devices: {devices_info}")

    except Exception as e:
        logging.error(f"Error creating table: {e}")


create_table([571, 572])
