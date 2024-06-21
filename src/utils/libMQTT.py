# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
import os
import sys
from pathlib import Path
import paho.mqtt.publish as publish

# ----- MQTT -----
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
def push_data_to_mqtt(host, port,topic,username, password, data_send,qos=0,retain=False):
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,qos=qos,
                    retain=retain, port=port,
                    auth = {'username':f'{username}', 
                            'password':f'{password}'})
        # publish.single(Topic, payload, hostname=Broker,
        #             retain=False, port=Port)
    # except Error as err:
    #     print(f"Error MQTT public: '{err}'")
    except Exception as err:
    # except:
        
        print(f"Error MQTT public: '{err}'")
        pass