class Query():
    select_upload_channel="""
        SELECT 
        upload_channel.id,upload_channel.name ,
        config_information.namekey as type_protocol,
	    upload_channel.enable
        FROM upload_channel 
        INNER JOIN config_information ON config_information.id=upload_channel.id_type_protocol 
        Where  upload_channel.id ={id_upload_channel};
    """
all_query=Query()