class Query():
    select_all_device="""
        SELECT device_list.id, device_list.name, 
        driver_list.name AS connect_type, 
        device_type.name AS device_type_name,
        device_list.id_communication AS id_communication
        FROM device_list
        INNER JOIN device_type ON device_list.id_device_type=device_type.id
        INNER JOIN communication ON device_list.id_communication=communication.id
        INNER JOIN driver_list ON communication.id_driver_list=driver_list.id 
        WHERE device_list.status=1;
        """
    add_sld_group="""
        INSERT INTO sld_group (name, type)
        VALUES ("{name}",{group_type});
    """
    # update_sld_group="""
    #     INSERT INTO sld_group (name, type)
    #     VALUES ("{name}",{group_type});
    # """
    # add_sld_group_inv="""
    #     INSERT INTO id_sld_group (id_sld_group, id_device_list)
    #     VALUES ("{id_sld_group}",{id_device});
    # """
    # add_sld_group_meter="""
    #     INSERT INTO id_sld_group (id_sld_group, id_device_list)
    #     VALUES ("{id_sld_group}",{id_device});
    # """
all_query=Query()