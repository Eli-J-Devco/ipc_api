# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import json
import os
import sys
import time
from datetime import datetime as DT
from pprint import pprint

arr = sys.argv
print(f'arr: {arr}')
async def log(arr):
    print(f'Restart Device : {arr[1]}')
    while True:
        print(f'Device: {arr[1]}')
        await asyncio.sleep(2)
async def main():
    tasks = []
    tasks.append(asyncio.create_task(log(arr)))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())