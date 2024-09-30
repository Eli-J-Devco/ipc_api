class Query():
    
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
query_all=Query()