class Query():
    
    select_ethernet="""
        SELECT device_list.id, device_list.name, 
        driver_list.name AS connect_type, 
        device_type.name AS device_type,
        device_list.id_communication AS id_communication,
        device_list.rtu_bus_address AS rtu_bus_address,
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
        
        WHERE device_list.status=1 and device_list.id_communication ={id_communication};
    """
    select_upload_channel="""
        SELECT 
        upload_channel.id,upload_channel.name ,
        config_information.namekey as type_protocol,
	    upload_channel.enable
        FROM upload_channel 
        INNER JOIN config_information ON config_information.id=upload_channel.id_type_protocol 
        Where  upload_channel.id ={id_upload_channel};
    """
    select_all_upload_channel="""
        SELECT 
        upload_channel.id,upload_channel.name ,
        config_information.namekey as type_protocol,
	    upload_channel.enable
        FROM upload_channel 
        INNER JOIN config_information ON config_information.id=upload_channel.id_type_protocol 
        Where  upload_channel.status ={status};
    """
all_query=Query()