class Query():
    select_all_device="""
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
    select_point_list=""""
        SELECT  

        device_point_list_map.id,
        point_list.id_pointkey AS pointkey,
        point_list_type.id AS id_point_list_type,
        point_list_type.namekey AS name_point_list_type,
        
        table_pointtype.name AS pointtype,
        point_list.id_pointclass_type AS id_pointclass,
        point_list.id_config_information AS id_config_infor,
        point_list.id_pointtype AS id_pointtype,
        
        table_pointclass_type.name AS class,
        table_config_information.namekey AS config_information,
        point_list.id AS id_point,
        point_list.parent AS parent,
        device_point_list_map.name,
        device_point_list_map.low_alarm,
        device_point_list_map.high_alarm,
        driver_list.name AS connect_type,
        device_type.name AS device_type, 
        device_group.name AS device_group,
        
        template_library.name AS template_name,
        template_library.id AS id_template,
        device_group.id AS id_device_group,
        device_point_list_map.id_device_list,
        device_point_list_map.id_point_list,
        
        point_list.id_pointkey AS id_pointkey,
        point_list.name AS point_name,
        point_list.nameedit,
        point_list.id_type_units,
        point_list.nameedit,
        point_list.unitsedit,

        point_list.register,
        point_list.id_type_datatype,
        point_list.id_type_byteorder,
        point_list.slope,
        point_list.slopeenabled,
        point_list.offset,
        point_list.offsetenabled,
        point_list.multreg,
        point_list.multregenabled,
        point_list.userscaleenabled,
        point_list.invalidvalue,
        point_list.invalidvalueenabled,
        point_list.extendednumpoints,
        point_list.extendedregblocks,

        
	
        table_byteorder.value AS value_byteorder,
        table_byteorder.namekey AS name_byteorder,
        table_datatype.value AS value_datatype,
        table_datatype.namekey AS name_datatype,
        table_units.value AS value_units,
        table_units.namekey AS name_units,
        point_list.active AS `active`,
        point_list.id_control_group,
        point_list.control_type_input,
        point_list.control_menu_order,
        point_list.control_min,
        point_list.control_max,
        device_panel.height as panel_height,
        device_panel.width as panel_width
        FROM `device_point_list_map` 
        INNER JOIN point_list ON device_point_list_map.id_point_list=point_list.id
        LEFT JOIN point_list_type ON point_list_type.id=point_list.id_point_list_type
        
        INNER JOIN device_list  ON device_point_list_map.id_device_list=device_list.id
        INNER JOIN template_library ON device_list.id_template=template_library.id
        
        INNER JOIN device_group ON template_library.id_device_group=device_group.id
        
        INNER JOIN device_type  ON device_type.id=device_list.id_device_type
        INNER JOIN communication ON communication.id=device_list.id_communication
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id
        
        INNER JOIN config_information table_byteorder ON point_list.id_type_byteorder=table_byteorder.id
        INNER JOIN config_information table_datatype ON point_list.id_type_datatype=table_datatype.id
        LEFT JOIN config_information table_units ON point_list.id_type_units=table_units.id
        LEFT JOIN pointclass_type table_pointclass_type ON point_list.id_pointclass_type=table_pointclass_type.id
        LEFT JOIN config_information table_config_information ON point_list.id_config_information=table_config_information.id
        LEFT JOIN config_information table_pointtype ON point_list.id_pointtype=table_pointtype.id
        LEFT JOIN point_list_control_group  ON point_list.id_control_group=point_list_control_group.id
        
        Left JOIN device_panel  ON device_panel.id_point_list=device_point_list_map.id_point_list and device_panel.id_device_list=device_point_list_map.id_device_list
        
        WHERE device_point_list_map.status=1 AND
                    device_point_list_map.id_device_list={id_device} ORDER BY device_point_list_map.id ASC;
        """
    select_register_block="""
        SELECT 
        register_block.id,
        register_block.id_template,
        template_library.name AS template_name,
        register_block.addr AS addr,
        register_block.count AS `count`,
        config_information.namekey AS namekey,
        config_information.value AS Functions
        FROM register_block
        INNER JOIN template_library ON register_block.id_template=template_library.id
        INNER JOIN config_information ON register_block.id_type_function=config_information.id
        
        WHERE register_block.status=1 AND
                    register_block.id_template={id_template} ORDER BY register_block.id ASC;
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
        device_list.id_communication AS id_communication,
        device_list.rtu_bus_address AS rtu_bus_address,
        device_list.id_template,
        communication.name AS serialport_name,
        communication.namekey AS serialport_group,
        table_baud.name AS serialport_baud,
        table_parity.name AS serialport_parity,
        table_stopbits.name AS serialport_stopbits,
        table_timeout.name AS serialport_timeout,
        table_debug_level.name AS serialport_debug_level,
        device_group.name AS device_group,
        template_library.name AS template_name,
        device_list.rated_power,
        device_list.rated_power_custom,
        device_list.min_watt_in_percent
        
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
    
all_query=Query()