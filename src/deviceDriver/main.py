import asyncio
import datetime
import json
import sys

import mqttools
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException


class driverGateway:
    def __init__(self,
                SERIAL_NUMBER,
                MQTT_BROKER="127.0.0.1",
                MQTT_PORT=1883,
                MQTT_USERNAME="",
                MQTT_PASSWORD="",
                        **kwargs):
        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOPIC = SERIAL_NUMBER
        self.MQTT_USERNAME = MQTT_USERNAME
        self.MQTT_PASSWORD = MQTT_PASSWORD
        
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
    async def handle_messages_drivers(self,client):
        try :
            # 
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                print(message)
                result=json.loads(message.message.decode())
                if 'code' in result.keys() and 'payload' in result.keys():
                    if result["code"]=="add_job":
                        job_id=result["payload"]
                        print(job_id)
                        self.scheduler.add_job(
                        this_job,
                        # "cron",
                        'interval',
                        id=f"{job_id}",
                        # second = f'*/2',
                        seconds = 3,
                        args=[job_id,self.MQTT_TOPIC]
                        )
                        pass
                    if result["code"]=="remove_job":  
                        job_id=result["payload"] 
                        self.scheduler.remove_job(job_id=f"{job_id}")
                    if result["code"]=="pause_job":
                        job_id=result["payload"] 
                        self.scheduler.pause_job(job_id=f"{job_id}")
                    if result["code"]=="resume_job":
                        job_id=result["payload"] 
                        self.scheduler.resume_job(job_id=f"{job_id}")
                    if result["code"]=="pause":  
                        self.scheduler.pause()
                    if result["code"]=="resume":  
                        self.scheduler.resume()
        except Exception as err:
            print(f"Error handle_messages_drivers: '{err}'") 

    async def managerDrivers(self):
        try:
                
            Topic=f'{self.MQTT_TOPIC}/Init/Drivers'                
            client = mqttools.Client(host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            subscriptions=[Topic],
                            password=bytes(self.MQTT_PASSWORD, 'utf-8'),
                            connect_delays=[1, 2, 4, 8]
                            )
            while True:
                await client.start()
                await self.handle_messages_drivers(client)
                await client.stop()
        except Exception as err:
            print(f"Error managerDrivers: '{err}'")   
async def main():
    tasks = []
    
    SERIAL_NUMBER="G83VZT33"
    MQTT_BROKER="127.0.0.1"
    MQTT_PORT=1883
    MQTT_USERNAME="nextwave"
    MQTT_PASSWORD="123654789"
    api_gateway=driverGateway(
                            SERIAL_NUMBER,
                            MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            )
    tasks.append(asyncio.create_task(
        api_gateway.managerDrivers()))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('Drivers GATEWAY stopped.')
        sys.exit(0)