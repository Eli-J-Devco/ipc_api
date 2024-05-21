# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pathlib import Path
import netifaces
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

from .ethernet_model import EthernetConfig, EthernetDetails
from ..config import env_config


class NetworkInterfaceConfig:
    _default_type_ethernet = "dhcp"

    def __init__(self, nic: EthernetConfig = None):
        self._namekey = nic.namekey
        self._allow_dns = nic.allow_dns
        self._ip_address = nic.ip_address
        self._subnet_mask = nic.subnet_mask
        self._gateway = nic.gateway
        self._mtu = nic.mtu
        self._dns1 = nic.dns1
        self._dns2 = nic.dns2

    def to_dict(self):
        return {
            "namekey": self._namekey,
            "allow_dns": self._allow_dns,
            "ip_address": self._ip_address,
            "subnet_mask": self._subnet_mask,
            "gateway": self._gateway,
            "mtu": self._mtu,
            "dns1": self._dns1,
            "dns2": self._dns2
        }

    def get_network_config(self):
        ipaddress = netifaces.ifaddresses(self._namekey)
        if netifaces.AF_INET in ipaddress:
            print(ipaddress[netifaces.AF_INET])
            self._ip_address = ipaddress[netifaces.AF_INET][0]['addr']
            self._subnet_mask = ipaddress[netifaces.AF_INET][0]['netmask']
            self._gateway = ipaddress[netifaces.AF_INET][0]['broadcast']
        return self.to_dict()


class UpdateNetworkInterfaceConfig(NetworkInterfaceConfig):
    def __init__(self, ethernet: EthernetDetails = None):
        super().__init__(EthernetConfig(**ethernet.__dict__))
        self._id = ethernet.id
        self._name = ethernet.name
        self._type_ethernet_name = ethernet.type_ethernet.name

    def to_dict(self):
        dhcp = "yes" if self._type_ethernet_name == super()._default_type_ethernet else "no"
        addresses = None if self._type_ethernet_name == super()._default_type_ethernet else [f"{self._ip_address}/24"]
        gateway4 = None if self._type_ethernet_name == super()._default_type_ethernet else self._gateway
        dns = None if self._type_ethernet_name == super()._default_type_ethernet \
            else [self._dns1, self._dns2] if self._allow_dns else []

        output = {
            "dhcp4": dhcp,
        }
        if addresses:
            output["addresses"] = addresses
        if gateway4:
            output["gateway4"] = gateway4
        if dns:
            output["nameservers"] = {"addresses": dns}
        return output

    def create_network_config(self, output_path: str):
        try:
            config_data = load(open(output_path, 'r'), Loader=Loader)
        except FileNotFoundError:
            config_data = load(open(self.get_network_config_sample(), 'r'), Loader=Loader)
        except Exception as e:
            raise e

        if not config_data:
            raise Exception("Network configuration file is empty")

        if "network" not in config_data:
            config_data["network"] = {}
            config_data["network"]["version"] = 2

        if "ethernets" not in config_data["network"]:
            config_data["network"]["ethernets"] = {}

        config_data["network"]["ethernets"][self._namekey] = self.to_dict()

        self.write_network_config(output_path, config_data)

    @staticmethod
    def get_network_config_sample():
        return Path(__file__).resolve().parent.__str__() + env_config.PATH_FILE_NETWORK_SAMPLE

    @staticmethod
    def write_network_config(output_path: str, config_data: dict):
        config_data = dump(config_data, Dumper=Dumper, sort_keys=False)
        config_data = (config_data
                       .replace("'", "")
                       .replace("true", "yes")
                       .replace("false", "no")
                       .replace("\'yes\'", "yes")
                       .replace("\'no\'", "no"))

        with open(output_path, 'w+') as file:
            file.write(config_data)
