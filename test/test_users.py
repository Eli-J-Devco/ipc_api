# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pprint import pprint

import requests
from jose import jwt

algorithm = "HS256"
secret_key = "25a6f201f7f43132035d95e1b0125ec3f937ec284bd93e6f4ad17078b75b3cdf"
REFRESH_SECRET_KEY="4845118e9928805aea99b052f2ef7426c885325a109bed4171a84303b9594e8d"
refresh_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1NCwiZXhwIjoxNzA5MjcxMDIzfQ.H3SVg_Vb4Yw2-Guhhci2GeLy2fPdbEyFJ4yjZTIoIgA'
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1NCwiZXhwIjoxNzA4NjY5ODIzfQ.JjCNZW3fOg_IsxZV3u9htUHB_jnUFGW7Q8WdkSDeZeI'


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
    API_ENDPOINT = "http://192.168.1.21:3001/login/"
    payload = {
        # 'username': 'nguyenvudtd@gmail.com',
        # 'password': 'Admin123@'
        'username':"U2FsdGVkX197XjIeAGjbF5iI1z0t0fveHsBafkByeA+t+44x/0NgQDU8se53AHiD",
        'password': "U2FsdGVkX18tV9IZbkHv1wDVLx3Rxs93stKcKiA/Dz0="
    }
    # sending post request and saving response as response object
    # headers = {"Content-Type": "application/json; charset=utf-8"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url=API_ENDPOINT, data=payload, headers=headers)

    # extracting response text
    data = r.json()
    pprint("The pastebin URL is:%s" % data, sort_dicts=False)
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
    # payload = jwt.decode(access_token,
    #                      secret_key, algorithms=[algorithm])
    # print(payload)
    user_id = 50 #payload['user_id']
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
        "email": "nguyenvudtd@gmail.com",
        "password": "123456",
        "fullname": "vnguyen",
        "phone": "",
        "id_language": 1,
        "id":50
        # "owner_id": 2,
    }
    # response = requests.post(
    #     'http://127.0.0.1:8000/device_list/delete/', headers=headersAuth, json=data, verify=True)
    response = requests.post(
        'http://127.0.0.1:8000/users/update/?id=50', headers=headersAuth,json=data, verify=True)
    j = response.json()
    print(j)

def test_refresh_token():
    # Test OK
    # defining the api-endpoint
    API_ENDPOINT = "http://192.168.1.21:3001/refresh_token/"
    payload = {
        'refresh_token': refresh_token
    }
    # sending post request and saving response as response object
    # headers = {"Content-Type": "application/json; charset=utf-8"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response= requests.post(url=API_ENDPOINT, json=payload)

    # extracting response text
    data = response.json()
    pprint("The pastebin URL is:%s" % data)
    # payload = jwt.decode(login_res.access_token,
    #   
# # test_create_user()
test_login_user()
# test_create_posts()
# test_get_one_post()
# decode_token()
# test_update_post()
# test_refresh_token()
# test_update_post()