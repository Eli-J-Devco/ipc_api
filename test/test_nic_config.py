import netifaces

from ..src.ethernet.ethernet_helper import NetworkInterfaceConfig, UpdateNetworkInterfaceConfig


if __name__ == "__main__":
    # network_interface = {
    #     "id_ethernet": 2,
    #     "namekey": "eth1",
    #     "id_type_ethernet_name": "dhcp",
    #     "ip_address": "",
    #     "gateway": "",
    #     "allow_dns": False,
    #     "dns1": "",
    #     "dns2": ""
    # }
    # network_interface = UpdateNetworkInterfaceConfig(**network_interface)
    # network_interface.create_network_config("D:\\Nhan\\network.yaml")
    interfaces = netifaces.interfaces()
    builtin_nics = []
    for interface in interfaces:
        print("============Address================")
        print(netifaces.ifaddresses(interface))
        print("===================================")
        builtin_nics.append(NetworkInterfaceConfig(namekey=interface).get_network_config())

    print("===========Builtin============")
    print(builtin_nics)
    print("==============================")
