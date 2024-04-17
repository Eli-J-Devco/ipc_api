# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import base64
import logging
from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Cryptodome import Random
from Cryptodome.Cipher import AES
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Describe functions before writing code
# /**
# 	 * @description hash password
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {password}
# 	 * @return data (password)
# 	 */
def hash_password(password: str):
    return pwd_context.hash(password)


# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 22-12-2023
# 	 * @param {auth}
# 	 * @return data (or_auth)
# 	 */
def convert_binary_auth(auth):
    try:
        result_auth = ""
        for i, item in enumerate(auth):
            if i < len(auth) - 1:
                result_auth = result_auth + str(item) + "|"
            else:
                result_auth = result_auth + str(item)
        if not result_auth:
            return 0
        else:
            return int(bin(eval(result_auth)), 2)
    except Exception as err:
        print('Convert_binary_auth: ' + str(err))
        return 0


# Describe functions before writing code
# /**
# 	 * @description verify password
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {plain_password, hashed_password}
# 	 * @return data (password verify)
# 	 */
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


BLOCK_SIZE = 16


def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length) * length).encode()


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
    try:
        salt = Random.new().read(8)
        key_iv = bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))
    except Exception as err:
        raise err


def decrypt(encrypted, passphrase):
    try:
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return unpad(aes.decrypt(encrypted[16:]))
    except Exception as err:
        raise err
