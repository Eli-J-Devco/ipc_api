import asyncio
import json
# from controllers import bar, foo
from datetime import datetime

import mqttools
import paho.mqtt.publish as publish
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def func_mqtt_public(host, port,topic, username, password, data_send):
    try:
        payload = json.dumps(data_send)
      
        publish.single(topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})

    except Exception as err:
        print(f"Error MQTT public: '{err}'")
async def foo(value):
    print(f'foo: ---------------------------------------------------- {value}')
    print(f'{datetime.now()} Foo')

data=0

async def bar2():
    while True:
        # print('bar2: ----------------------------------------------------')
        global data
        data +=1
        # print(data)
        # print(f'{datetime.now()} Bar2')
        MQTT_BROKER = "127.0.0.1"
        MQTT_PORT = 1883
        MQTT_TOPIC = "IPC"
        MQTT_USERNAME = "nextwave"
        MQTT_PASSWORD = "123654789"
        func_mqtt_public(MQTT_BROKER,MQTT_PORT,MQTT_TOPIC,MQTT_USERNAME,MQTT_PASSWORD,data)
        await asyncio.sleep(5)
async def main():
    # Init message
    print('\nPress Ctrl-C to quit at anytime!\n')
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(foo, 'cron', second="*/1",args=["111"])
    scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
    # scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
    scheduler.start()
    # 
    tasks = []
    # tasks.append(asyncio.create_task(bar1()))
    tasks.append(asyncio.create_task(bar2()))
    await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.create_task(main())
    # loop.run_forever()
    asyncio.run(main())