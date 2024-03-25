import mqttools
import paho.mqtt.client as mqtt
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Information MQTT

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = "1883"
MQTT_TOPIC = "IPC"
MQTT_USERNAME = "nextwave"
MQTT_PASSWORD = "123654789"
MQTT_TOPIC_SUB = "IPC/Control/#"

id_device = ""
device_name = ""
status_control_request = ""

async def mqtt_subscribe_controlsV2(host, port, topic, username, password):
    global device_control
    global device_name
    global enable_write_control
    
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topic)
        
        while True:
            try:
                message = await asyncio.wait_for(client.messages.get(), timeout=5.0)
            except asyncio.TimeoutError:
                print("Timeout: No message received within 5 seconds")
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            mqtt_result = json.loads(message.message.decode())
            
            if mqtt_result:
                if 'ID_DEVICE' not in mqtt_result or 'DEVICE_NAME' not in mqtt_result or 'STATUS_CONTROL_REQUEST' not in mqtt_result:
                    continue

                device_control = mqtt_result['ID_DEVICE']
                device_name = mqtt_result['DEVICE_NAME']
                enable_write_control = mqtt_result['STATUS_CONTROL_REQUEST']
                
                print(f"device_control {device_control}, device_name {device_name}, enable_write_control {enable_write_control}")
                
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
        
async def main():
    # share variable
    global MQTT_BROKER
    global MQTT_PORT
    global MQTT_TOPIC_SUB
    global MQTT_USERNAME
    global MQTT_PASSWORD
    
    # Create task run async
    tasks = []
    tasks.append(mqtt_subscribe_controlsV2(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_TOPIC_SUB,
                            MQTT_USERNAME,
                            MQTT_PASSWORD
                            ))
    
    await asyncio.gather(*tasks, return_exceptions=False)
    #-------------------------------------
    await asyncio.sleep(0.05)
if __name__ == "__main__":
    asyncio.run(main())