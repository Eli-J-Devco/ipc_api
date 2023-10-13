import requests
from jose import jwt
# access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTcxMjk3NTd9.TgD8dqoSGaLnJb6GX7-H6fGu3vAkqv-BQM2vuDua27E"
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE2OTcxMzEzNzJ9.J0OYnUTI8fnYI5UMxZy6nSxiUxfmlSnek3QOvv-yGJw'
secret_key = "09d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7"
algorithm = "HS256"


def test_login_user():
    # defining the api-endpoint
    API_ENDPOINT = "http://127.0.0.1:8000/login"
    payload = {'username': 'nguyenvudtd@gmail.com',
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


# test_login_user()
def decode_token():
    payload = jwt.decode(access_token,
                         secret_key, algorithms=[algorithm])
    # "WWW-Authenticate": "Bearer"
    headersAuth = {
        # 'WWW-Authenticate': 'Bearer ' + str(access_token),
        'Authorization': 'Bearer ' + str(access_token),
    }
    print(payload)
    data = {
        "title": "vu",
        "content": "vu",
        "published": True
    }
    response = requests.post(
        'http://127.0.0.1:8000/posts', headers=headersAuth, data=data, verify=True)
    j = response.json()
    print(j)


decode_token()
# {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTcxMjk3NTd9.TgD8dqoSGaLnJb6GX7-H6fGu3vAkqv-BQM2vuDua27E',
#  'token_type': 'bearer'}
