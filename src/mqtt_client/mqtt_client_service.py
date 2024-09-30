import base64
import datetime
import gzip
import json
from typing import Optional, Any
import paho.mqtt.publish as publish
from src.mqtt_client.mqtt_client_model import MQTTConfigBase ,MQTTMsgs,MQTTMsg

class MQTTClientService:
    def __init__(self, mqtt_config:MQTTConfigBase,
                 **kwargs):
        self.host=mqtt_config.host
        self.port=mqtt_config.port
        self.username=mqtt_config.username
        self.password=mqtt_config.password
    def public_paho_zip(self, 
                        topic: str="",
                        message: Any=None,
                        ):
        try:
            
            publish.single( topic, 
                            payload=message, 
                            hostname=self.host,
                            retain=False, 
                            port=self.port,
                            auth = {'username':f'{self.username}', 
                                    'password':f'{self.password}'})
        
        except Exception as err:
            print(f"Error mqtt_public_paho_zip: '{err}'") 
        finally:
            pass
    def public_multi_paho_zip(self, 
                        messages: MQTTMsgs,
                        encode: bool=False,
                        ):
        try:
            # msgs = [{'topic': "paho/test/multiple1", 'payload': "multiple 1"}, 
            #         {'topic': "paho/test/multiple2", 'payload': "multiple 2"}]
            msgs=[]
            if messages.msgs:
                
                if encode:
                    for msg in messages.msgs:
                        
                        if type(msg.payload)==list:
                            payload=[]
                            for item in msg.payload:
                                payload.append(item.dict())
                            payload=json.dumps(payload)
                            
                            gzip_compress = gzip.compress(payload.encode("ascii"), 9)
                            payload=base64.b64encode(gzip_compress)
                            msgs.append({**msg.__dict__,"payload":payload} )
                        else:
                            
                            gzip_compress = gzip.compress(msg.payload.json(indent=4).encode("ascii"), 9)
                            payload=base64.b64encode(gzip_compress)
                            msgs.append({**msg.__dict__,"payload":payload} )
                        
                else:
                    for msg in messages.msgs:
                        if type(msg.payload)==list:
                            payload=[]
                            for item in msg.payload:
                                payload.append(item.dict())
                            payload=json.dumps(payload)
                            msgs.append({**msg.__dict__,"payload":payload} )
                        else:
                            msgs.append({**msg.__dict__,"payload":msg.payload.json()} )
                # print(f'msgs: {msgs}')     
                publish.multiple(msgs, 
                                hostname=self.host,
                                port=self.port,
                                auth = {'username':f'{self.username}', 
                                        'password':f'{self.password}'}
                                )
        except Exception as err:
            print(f"Error public_multi_paho_zip: '{err}'") 
        finally:
            pass
        
        