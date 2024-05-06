class Query():
    select_device_through_template="""
        SELECT device_list.id, device_list.name,
        device_list.mode,
        device_list.id_template,
        communication.namekey AS serialport_group,
        device_list.id_communication,
        device_list.value_p, device_list.send_p,
        device_list.rtu_bus_address AS rtu_bus_address,
        device_list.tcp_gateway_ip AS tcp_gateway_ip,
        device_list.tcp_gateway_port AS tcp_gateway_port,
        device_list.point_p,device_list.value_p,device_list.send_p,
        device_list.point_q,device_list.value_q,device_list.send_q,
        device_list.point_pf,device_list.value_pf,device_list.send_pf,
        device_list.enable_poweroff, device_list.inverter_shutdown,
        driver_list.name AS connect_type, 
        device_type.name AS device_type,
        device_type.id AS id_device_type,
        device_group.name AS device_group,
        template_library.name AS template_name,
        device_list.rated_power,
        device_list.rated_power_custom,
        device_list.min_watt_in_percent

        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id      
        
        INNER JOIN template_library ON template_library.id=device_list.id_template
        INNER JOIN device_group ON device_group.id=template_library.id_device_group
        WHERE device_list.status=1 and
        device_list.id_template={id_template};
    """
    
    
all_query=Query()