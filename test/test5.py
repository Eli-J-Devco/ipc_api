

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
import binascii
# if platform.system() == 'linux':
#     # load_dotenv('.env.production')
#     print(".env.production")
# else:
#     # load_dotenv('.env.development')
#     print(".env.production")
import hashlib
import os
import platform
import random
import string
from base64 import b64decode, b64encode
from hashlib import md5, sha256

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Cryptodome import Random
from Cryptodome.Cipher import AES

# from AESify import AESify
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# from Cryptodome.Cipher import AES
# from Cryptodome.Random import get_random_bytes
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# from config import *

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

# salt = os.urandom(16)
# kdf = PBKDF2HMAC(
#     algorithm=hashes.SHA256(),
#     length=32,
#     salt=salt,
#     iterations=390000,
# )
# password = b"1"
# token = b"@qua$weet@NW"
# # key= base64.urlsafe_b64encode(kdf.derive(password))
# key =b'7ZvQ1c52jX4wJw1MWgiEkCjFOQhkg3LdTgmhzmf5vnQ='

# f = Fernet(key)
# # --------------------
# print(f'key: {key.decode()}')
# encMessage = f.encrypt(password)

# print(f'Ma hoa {encMessage.decode()}')
# decMessage = f.decrypt(encMessage)
# giaima=decMessage.decode('utf-8')
# print(f'Giai ma {giaima}')






#AES ECB mode without IV



BLOCK_SIZE = 16

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))


password = "4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a".encode()
# ct_b64 = "U2FsdGVkX1+ATH716DgsfPGjzmvhr+7+pzYfUzR+25u0D7Z5Lw04IJ+LmvPXJMpz"
ct_b64 = "U2FsdGVkX1+LKFFEChpO6bcHGHDwJ+yMm0ts1c2Lnik="
pt = decrypt(ct_b64, password)
print("pt", pt)
username=encrypt(b"vnguyen@nwemon.com",password)
print("username", username)
passwords=encrypt(b"Admin123@",password)
print("passwords", passwords)
# print("pt", decrypt(encrypt(pt, password), password))