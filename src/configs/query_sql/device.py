class Query():
    select_all_device="""
        SELECT device_list.id, 
        device_list.name, 
        driver_list.name AS connect_type, 
        device_type.name AS device_type,
        device_type.type AS `type`,
        device_list.id_communication AS id_communication,
        communication.name AS serialport_name,
        communication.namekey AS serialport_group,
        table_baud.name AS serialport_baud,
        table_parity.name AS serialport_parity,
        table_stopbits.name AS serialport_stopbits,
        table_timeout.name AS serialport_timeout,
        table_debug_level.name AS serialport_debug_level
        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id 
        LEFT JOIN config_information table_baud ON communication.id_type_baud_rates=table_baud.id
        LEFT JOIN config_information table_parity ON communication.id_type_parity=table_parity.id
        LEFT JOIN config_information table_stopbits ON communication.id_type_stopbits=table_stopbits.id
        LEFT JOIN config_information table_timeout ON communication.id_type_timeout=table_timeout.id
        LEFT JOIN config_information table_debug_level ON communication.id_type_debug_level=table_debug_level.id
        
        WHERE device_list.status=1;
        """
    select_only_device="""
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
        device_type.type AS device_type_value,
        device_group.name AS device_group,
        template_library.name AS template_name,
        device_list.rated_power,
        device_list.rated_power_custom,
        device_list.min_watt_in_percent

        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        LEFT JOIN communication ON device_list.id_communication=communication.id
        LEFT JOIN driver_list ON communication.id_driver_list=driver_list.id      
        
        LEFT JOIN template_library ON template_library.id=device_list.id_template
        LEFT JOIN device_group ON device_group.id=template_library.id_device_group
        WHERE 
        device_list.id={id_device};
        """
    select_only_device_use_driver="""
        SELECT device_list.id, 
        device_list.parent,
        device_list.name,
		device_list.mode,
		device_list.id_template,
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
        device_type.type AS type_device_type,
        device_group.name AS device_group,
        device_group.id AS id_device_group,
        template_library.name AS template_name,
        device_list.rated_power,
	    device_list.rated_power_custom,
	    device_list.min_watt_in_percent,
        device_list.meter_type,
        device_list.DC_voltage,
        device_list.DC_current,
        device_list.inverter_type,
        device_list.parent as device_parent,
        device_list.emergency_stop as emergency_stop
        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id      
        
        LEFT JOIN template_library ON template_library.id=device_list.id_template
        LEFT JOIN device_group ON device_group.id=template_library.id_device_group
        WHERE 
        device_list.id={id_device};
    """
    select_all_device_communication:str="""
        SELECT device_list.id, device_list.name, 
        driver_list.name AS connect_type, 
        device_type.name AS device_type,
        device_list.id_communication AS id_communication,
        communication.name AS serialport_name,
        communication.namekey AS serialport_group,
        table_baud.name AS serialport_baud,
        table_parity.name AS serialport_parity,
        table_stopbits.name AS serialport_stopbits,
        table_timeout.name AS serialport_timeout,
        table_debug_level.name AS serialport_debug_level
        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id 
        LEFT JOIN config_information table_baud ON communication.id_type_baud_rates=table_baud.id
        LEFT JOIN config_information table_parity ON communication.id_type_parity=table_parity.id
        LEFT JOIN config_information table_stopbits ON communication.id_type_stopbits=table_stopbits.id
        LEFT JOIN config_information table_timeout ON communication.id_type_timeout=table_timeout.id
        LEFT JOIN config_information table_debug_level ON communication.id_type_debug_level=table_debug_level.id
        
        WHERE device_list.status=1 AND device_list.id_communication={id_communication};
        """
    select_all_device_rs485:str="""
        SELECT device_list.id, device_list.name,
        device_list.mode,
        driver_list.name AS connect_type, 
        device_type.name AS device_type,
        device_type.id AS id_device_type,
        device_type.type AS type_device_type,
        device_list.id_communication AS id_communication,
        device_list.rtu_bus_address AS rtu_bus_address,
        device_list.id_template,
        device_list.enable_poweroff, device_list.inverter_shutdown,
        communication.name AS serialport_name,
        communication.namekey AS serialport_group,
        table_baud.name AS serialport_baud,
        table_parity.name AS serialport_parity,
        table_stopbits.name AS serialport_stopbits,
        table_timeout.name AS serialport_timeout,
        table_debug_level.name AS serialport_debug_level,
        device_group.name AS device_group,
        device_group.id AS id_device_group,
        template_library.name AS template_name,
        device_list.rated_power,
        device_list.rated_power_custom,
        device_list.min_watt_in_percent,
        device_list.meter_type,
        device_list.DC_voltage,
        device_list.DC_current,
        device_list.inverter_type,
        device_list.parent as device_parent,
        device_list.emergency_stop as emergency_stop
        
        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id 
        LEFT JOIN config_information table_baud ON communication.id_type_baud_rates=table_baud.id
        LEFT JOIN config_information table_parity ON communication.id_type_parity=table_parity.id
        LEFT JOIN config_information table_stopbits ON communication.id_type_stopbits=table_stopbits.id
        LEFT JOIN config_information table_timeout ON communication.id_type_timeout=table_timeout.id
        LEFT JOIN config_information table_debug_level ON communication.id_type_debug_level=table_debug_level.id
        
        INNER JOIN template_library ON template_library.id=device_list.id_template
        INNER JOIN device_group ON device_group.id=template_library.id_device_group
        
        WHERE device_list.status=1 AND device_list.id_communication ={id_communication};
    """
    select_all_device_mqtt_gateway:str="""
        select 
        device_list.id, 
        device_list.name,
        device_list.mode,
        device_list.efficiency,
        device_list.parent, 
        device_list.inverter_type,
        device_list.meter_type,
        device_type.name as name_device_type,
        device_type.type AS type_device_type
        from `device_list` 
        LEFT JOIN device_type ON device_list.id_device_type=device_type.id
        where device_list.status=1;
    """
query_all=Query()