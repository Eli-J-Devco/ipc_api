class Query():
    select_point_list="""
        SELECT  

        device_point_list_map.id,
        point_list.id_pointkey AS pointkey,
        point_list_type.id AS id_point_list_type,
        point_list_type.namekey AS name_point_list_type,
        
        table_pointtype.name AS pointtype,
        point_list.id_pointclass_type AS id_pointclass,
        point_list.id_config_information AS id_config_infor,
        point_list.id_pointtype AS id_pointtype,
        
        table_pointclass_type.name AS pointclass,
        table_pointclass_type.name AS class,
        table_config_information.namekey AS config_information,
        point_list.id AS id_point,
        point_list.parent AS parent,
        device_point_list_map.name,
        device_point_list_map.low_alarm,
        device_point_list_map.high_alarm,
        device_point_list_map.output_values,
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
        
        table_type_function.value as func,
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
        device_point_list_map.control_min,
        device_point_list_map.control_max,
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
        # LEFT JOIN point_list_control_group  ON point_list.id_control_group=point_list_control_group.id
        LEFT JOIN config_information table_type_function ON point_list.id_type_function=table_type_function.id
        
        Left JOIN device_panel  ON device_panel.id_point_list=device_point_list_map.id_point_list and device_panel.id_device_list=device_point_list_map.id_device_list
        
        WHERE device_point_list_map.status=1 AND
                    device_point_list_map.id_device_list={id_device} ORDER BY device_point_list_map.id ASC;
        """
    select_point_list_control_group="""
        SELECT * FROM point_list_control_group WHERE id_template={id_template} AND status=1
        """
query_all=Query()