# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import requests
from jose import jwt

# access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTcxMjk3NTd9.TgD8dqoSGaLnJb6GX7-H6fGu3vAkqv-BQM2vuDua27E"
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozNCwiZXhwIjoxNjk3NTQwMjQ4fQ.CBCTpBRLFhQ9iKwd6rAXVuq9vdiol5H3fGWcw51YZ8E'
secret_key = "09d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7"
algorithm = "HS256"


def test_create_user():
    API_ENDPOINT = "http://127.0.0.1:8000/users"
    payload = {
        'email': 'vnguyen@nwemon.com',
        'password': '12345',
        'fullname': 'vnguyen',
        'phone': "0938849192",
        'id_language': 1,

        # 'date_joined': '2023-10-13 17:02:35'
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    r = requests.post(url=API_ENDPOINT, json=payload)
    data = r.json()
    print("The pastebin URL is:%s" % data)


def test_login_user():
    # Test OK
    # defining the api-endpoint
    API_ENDPOINT = "http://127.0.0.1:8000/login"
    payload = {
        'username': 'vnguyen@nwemon.com',
        'password': '12345'
    }
    # sending post request and saving response as response object
    headers = {"Content-Type": "application/json; charset=utf-8"}
    r = requests.post(url=API_ENDPOINT, data=payload)

    # extracting response text
    data = r.json()
    print("The pastebin URL is:%s" % data)
    # payload = jwt.decode(login_res.access_token,
    #                      settings.secret_key, algorithms=[settings.algorithm])


def test_create_posts():
    payload = jwt.decode(access_token,
                         secret_key, algorithms=[algorithm])

    headersAuth = {
        # 'WWW-Authenticate': 'Bearer ' + str(access_token),
        # "Accept": "application/json",
        # "Content_Type": "application/json",
        'Authorization': 'Bearer ' + str(access_token)
    }

    print(payload)
    data = {
        "title": "vu",
        "content": "vu",
        "published": 1,
        # "owner_id": 2,
    }
    response = requests.post(
        'http://127.0.0.1:8000/posts', headers=headersAuth, json=data, verify=True)
    j = response.json()
    print(j)


def test_get_one_post():
    payload = jwt.decode(access_token,
                         secret_key, algorithms=[algorithm])
    print(payload)
    user_id = payload['user_id']
    # Test OK
    headersAuth = {
        # 'WWW-Authenticate': 'Bearer ' + str(access_token),
        'Authorization': 'Bearer ' + str(access_token),
    }
    response = requests.get(
        f"http://127.0.0.1:8000/users/{user_id}", headers=headersAuth, verify=True)

    j = response.json()
    print(j)


def test_update_post():

    headersAuth = {
        # 'WWW-Authenticate': 'Bearer ' + str(access_token),
        # "Accept": "application/json",
        # "Content_Type": "application/json",
        'Authorization': 'Bearer ' + str(access_token)
    }

    # print(payload)
    data = {
        "title": "vu",
        "content": "vu",
        "published": 1,
        "id":333
        # "owner_id": 2,
    }
    # response = requests.post(
    #     'http://127.0.0.1:8000/device_list/delete/', headers=headersAuth, json=data, verify=True)
    response = requests.post(
        'http://127.0.0.1:8000/device_list/delete/?id=1', json=data, verify=True)
    j = response.json()
    print(j)


# test_create_user()
# test_login_user()
# test_create_posts()
# test_get_one_post()
# decode_token()
test_update_post()