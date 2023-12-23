

import os
import sys

# arr = sys.argv
# print(f'arr: {arr[1]}')

# def name():
#     # data=0
#     data=0
#     if True:
#         data=5
#     print(data)
# name()
# sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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
# print(Config.DATABASE_HOSTNAME)

import base64
# if platform.system() == 'linux':
#     # load_dotenv('.env.production')
#     print(".env.production")
# else:
#     # load_dotenv('.env.development')
#     print(".env.production")
import hashlib
import os
import platform
from hashlib import sha256

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import *

# print(Config.DATABASE_HOSTNAME)
# # if platform.node() == 'dev-machine':
# #     load_dotenv('.env.dev')
# # else:
# #     load_dotenv('.env.prod')
# print(hashlib.algorithms_available)
# data="333"
# print(sha256(data.encode('utf-8')).hexdigest())

# Put this somewhere safe!
# key = Fernet.generate_key()
# f = Fernet(key)
# token = f.encrypt(b"1")
# print(token)
# print(f.decrypt(token))

salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,
)
message = b"1"
password = b"@qua$weet@NW"
# key= base64.urlsafe_b64encode(kdf.derive(password))
key =b'yYGx967p94hCCUaeJnImSkNjYjXPgQ3yHCl3Qf3pFUc='
f = Fernet(key)
# --------------------
print(f'key: {key.decode()}')
encMessage = f.encrypt(message)
print(f'{encMessage.decode()}')
decMessage = f.decrypt(encMessage)
print(decMessage.decode('utf-8'))
