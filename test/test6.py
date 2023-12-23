# id=1
# id_hash=str(id)
# print(hashlib.sha256(id_hash.encode('utf-8')).hexdigest())
import asyncio
import base64
import hashlib
import os
import sys
import time

import schedule
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# key =b'yYGx967p94hCCUaeJnImSkNjYjXPgQ3yHCl3Qf3pFUc='
# f = Fernet(key)
# # --------------------
# print(f'key: {key.decode()}')
# encId=b'gAAAAABlglnup_tJ4yFt7GdoKdDedKGx3QXM8BOboApkp0GKFVquZX4TabosOuWj7DuUcdCofCXF2zCSR0mxO767sbvHqCJG_Q=='
# decMessage = f.decrypt(encId)
# print(decMessage.decode('utf-8'))
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime

from config import *
from libMySQL import *


def get_utc():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    # print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
      return -1
    result=path_os[0:int(index_os)+len(string_find)]
    # print("Path directory relative:", result)
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)

# def task(id):
#    print("Executing the script...")
#    time_insert_dev = get_utc()
#    print(time_insert_dev)
#    value_insert = (time_insert_dev, id ) 
#    MySQL_Insert_v2(f'dev_0000{str(id)}', 1 ,value_insert) 

# # schedule.every(10).seconds.do(task, id=2)
# # schedule.every(10).seconds.do(task, id=3)
# # schedule.every(10).seconds.do(task, id=4)
# # schedule.every().minute.at(":05").do(task, id=2)
# # schedule.every(5).seconds.until("00:47").do(task, id=2)
# schedule.every(5).minute.at(":00").do(task, id=2)

# while True:
#    schedule.run_pending()
# #    time.sleep(1)


from operator import *


def decimalToBinary(n): 
    return bin(n).replace("0b", "")
array_dec=[1,2,4,8,16]
array_bin=[]
# for item in array_dec:
#   print(item)
#   # array_bin.append(int(item,2))
# print(array_bin)
item1=bin(8)
item2=bin(1023)
print(item1)
print(item2)
# sum = bin(int(item1, 2) + int(item2, 2))
# print(sum[2:])
# print(int(sum[2:], 2))
# inputA = int('00100011',2)  # define binary number
# inputB = int('00101101',2)
# print(inputA)
# print(inputB)
# print(int(bin(1023 | 1023 |8),2))
# z = 45 & 20
# print(z)
# data=[item1,item2]
# print(sum(data))
# def or_array(array):
#   result = 0
#   for i in range(len(array)):
#     result = result | array[i]
#   return result
data=[1,2,4,8,16]
result=""
for i,item in enumerate(data):
  if i < len(data)-1:
    result=result + str(item)+"|"
  else:
    result=result + str(item)
print(result)

  
print(int(bin(eval(result)),2))

# print(bin(add(int(item1,2),int(item2,2))))
# print(item1)
# print(item2)
# print(item1+item2)
# x = bin(1023)[2:]
# y = bin(1023)[2:]
# print(x)
# print(y)
# z=bin(add(int(x, 2)+int(y, 2)))
# print(z)


