# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 
import bcrypt
from cryptography.fernet import Fernet
import binascii
import requests

tableCode = [
    {'value': '2ZS', 'id': '!'}, {'value': 'X3p', 'id': '“'}, {'value': 'imE', 'id': '#'}, {'value': 'EUT', 'id': '$'},
    {'value': 'XSh', 'id': '%'}, {'value': 'E5P', 'id': '&'}, {'value': 'WEj', 'id': '‘'}, {'value': '45Q', 'id': '('},
    {'value': 'iI1', 'id': ')'}, {'value': 't6x', 'id': '*'}, {'value': 'hd9', 'id': '+'}, {'value': 'jiJ', 'id': ','},
    {'value': 'UPw', 'id': '-'}, {'value': 'AxC', 'id': '.'}, {'value': 'Ywb', 'id': '/'}, {'value': 'aY8', 'id': '0'},
    {'value': 'mLR', 'id': '1'}, {'value': 'qae', 'id': '2'}, {'value': 'Xpg', 'id': '3'}, {'value': 'oS3', 'id': '4'},
    {'value': 'dTN', 'id': '5'}, {'value': 'jSC', 'id': '6'}, {'value': 'Dfz', 'id': '7'}, {'value': 'Sz1', 'id': '8'},
    {'value': 'Qu1', 'id': '9'}, {'value': 'i5E', 'id': ':'}, {'value': 'IQ6', 'id': ';'}, {'value': 'Qnn', 'id': '<'},
    {'value': 'ZPA', 'id': '='}, {'value': 'N9x', 'id': '>'}, {'value': 'oiI', 'id': '?'}, {'value': 'yU3', 'id': '@'},
    {'value': '46o', 'id': 'A'}, {'value': '7nE', 'id': 'B'}, {'value': 'wuQ', 'id': 'C'}, {'value': 'O1O', 'id': 'D'},
    {'value': 'SKy', 'id': 'E'}, {'value': 'r1H', 'id': 'F'}, {'value': 'aUW', 'id': 'G'}, {'value': 'Tew', 'id': 'H'},
    {'value': 'chh', 'id': 'I'}, {'value': '7FA', 'id': 'J'}, {'value': 'ekK', 'id': 'K'}, {'value': 'Ewp', 'id': 'L'},
    {'value': 'Oxa', 'id': 'M'}, {'value': 'T6g', 'id': 'N'}, {'value': 'xYx', 'id': 'O'}, {'value': 'gbz', 'id': 'P'},
    {'value': 'd4h', 'id': 'Q'}, {'value': '1Ow', 'id': 'R'}, {'value': 'Fw6', 'id': 'S'}, {'value': 'mor', 'id': 'T'},
    {'value': 'NDC', 'id': 'U'}, {'value': '7pm', 'id': 'V'}, {'value': 'Rn4', 'id': 'W'}, {'value': 'RVu', 'id': 'X'},
    {'value': 'dUW', 'id': 'Y'}, {'value': 'ic8', 'id': 'Z'}, {'value': 'aRm', 'id': '['}, {'value': 'po7', 'id': '\\'},
    {'value': 'tVA', 'id': ']'}, {'value': 'C5a', 'id': '^'}, {'value': 'G0m', 'id': '_'}, {'value': 'WHB', 'id': '`'},
    {'value': 'P91', 'id': 'a'}, {'value': 'cDf', 'id': 'b'}, {'value': '5Zp', 'id': 'c'}, {'value': 'pX5', 'id': 'd'},
    {'value': 'beG', 'id': 'e'}, {'value': 'sgd', 'id': 'f'}, {'value': '2Dl', 'id': 'g'}, {'value': 'YjH', 'id': 'h'},
    {'value': 'SQB', 'id': 'i'}, {'value': 'jJE', 'id': 'j'}, {'value': 'Gtw', 'id': 'k'}, {'value': 'JsK', 'id': 'l'},
    {'value': 'qfv', 'id': 'm'}, {'value': '5ty', 'id': 'n'}, {'value': 'BSm', 'id': 'o'}, {'value': 'Fbd', 'id': 'p'},
    {'value': 'xO7', 'id': 'q'}, {'value': 'W5R', 'id': 'r'}, {'value': 'ugh', 'id': 's'},{ 'value': 'nbs' , 'id': 't'},
	{'value': 'mgl', 'id': 'u'}, {'value': 'aqL', 'id': 'v'}, {'value': 'QJN', 'id': 'w'},{ 'value': 'X9d' , 'id': 'x'},
	{'value': 'lIB', 'id': 'y'}, {'value': 'Csm', 'id': 'z'}, {'value': 'uQ8', 'id': ''},{ 'value': 'EW7' , 'id': '|'},
	{'value': 'pP9', 'id': ''} , {'value': '5r3', 'id': '~'}, {'value': 'Nq0', 'id' :' '}]

def find_value_by_string(input_string):
    found_values = []
    for char in input_string:
        for item in tableCode:
            if item['id'] == char:
                found_values.append(item['value'])
                break
    return found_values
def main():
    while True:
        print("""
        1 - user_settings()
        2 - data_record()
        3 - config_device()
        4 - control_device()
        0 - Exit
        """)
        choosemain_menu = int(input("Enter the corresponding number of your choice: "))

        if choosemain_menu == 1:
            user_settings()
        elif choosemain_menu == 2:
            data_record()
        elif choosemain_menu == 3:
            config_device()
        elif choosemain_menu == 4:
            control_device()
        elif choosemain_menu == 0:
            print("Exited the program.")
            break
        else:
            print("Invalid selection")
        
def data_record():
    return
def config_device():
    return
def control_device():
    return
def user_settings():
    print("""
    1 - register()
    2 - login ()
    3 - delete()
    4 - update()
    5 - show_user()
    """)
    choose_user = int(input("Enter the corresponding number of your choice : "))

    if choose_user == 1:
        register()
    elif choose_user == 2:
        login()
    elif choose_user == 3 :
        delete_user()
    elif choose_user == 4 :
        update_password()
    elif choose_user == 5 :
        showuser( )
    else:
        print("Invalid selection")
# /**
# 	 * @description Login user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {taikhoannhap , matkhaunhap }
# 	 * @return data (payload, message)
# 	 */
def login():

    # Url
    server_url_dangnhap = "http://127.0.0.1:8000/login"

    # Send to information sever 
    taikhoannhap= input("Enter your login account:")
    matkhaunhap = input("Enter your login password:")

    # find value in tablecode and connet it into a string 
    found_values = find_value_by_string(matkhaunhap)

    if found_values:
        chuoi_value_kethop = ''.join(found_values)
        print(f"The entered password has been encoded into the table's string format : {chuoi_value_kethop}")
    else:
        print(f"No value found for string {matkhaunhap}")
    
    
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)

    # decode paswords recieved from client and store them in sql 
    matkhauki_mahoa = client_key.encrypt(chuoi_value_kethop.encode())
    matkhaugocguidi_hex = binascii.hexlify(matkhauki_mahoa).decode()
    # create a  dictionary sent to sever  . class InformationUser(BaseModel):/client_user: str/client_password: str 
    payload = {"taikhoannhap": taikhoannhap,"matkhaunhap": matkhaugocguidi_hex}
    # comand post send request to sever 
    response = requests.post(server_url_dangnhap, json=payload)
# /**
# 	 * @description Register user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {taikhoanki , matkhauki
# 	 * @return data (payload, message)
# 	 */
def register():
    # url
    server_url_dangki = "http://127.0.0.1:8000/register"
    taikhoanki =input("Register a new account name :")
    matkhauki =input("Register a new password: ")
     # find value in tablecode and connet it into a string 
    found_values = find_value_by_string(matkhauki)

    if found_values:
        chuoi_value_kethop = ''.join(found_values)
        print(f"The entered password has been encoded into the table's string format : {chuoi_value_kethop}")
    else:
        print(f"No value found for string {matkhauki}")
    # decode information 2 levels 
    # password defaults the same as in client
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)

    # decode password bcrypt with key Fernet
    matkhauki_mahoa = client_key.encrypt(chuoi_value_kethop.encode())
    print("passwword is decode is:", matkhauki_mahoa)
    matkhaugocguidi_hex = binascii.hexlify(matkhauki_mahoa).decode()
    print("information sent to sever :", matkhaugocguidi_hex)

    # create a  dictionary sent to sever  . class InformationUser(BaseModel):/client_user: str/client_password: str 
    payload = {"taikhoannhap": taikhoanki,"matkhaunhap": matkhaugocguidi_hex}

   # comand post send request to sever
    response = requests.post(server_url_dangki, json=payload)
# /**
# 	 * @description Delete user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {taikhoannhap , matkhaunhap }
# 	 * @return data (payload, message)
# 	 */
def delete_user():
    server_url_delete = "http://127.0.0.1:8000/delete"
    taikhoandelete =input("input accout need delete :")
    # create a  dictionary sent to sever  . class InformationUser(BaseModel):/client_user: str/client_password: str 
    payload = {"taikhoanxoa": taikhoandelete}
    # comand post send request to sever
    response = requests.post(server_url_delete, json=payload)
    # /**
# 	 * @description show user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {,}
# 	 * @return data (json, message)
# 	 */
def showuser():
    #url
    server_url_show = "http://127.0.0.1:8000/show"
    # comand post send request to sever
    response = requests.post(server_url_show)
# /**
# 	 * @description update user
# 	 * @author binhnguyen
# 	 * @since 09-15-2023
# 	 * @param {taikhoannhap , matkhaunhap }
# 	 * @return data (payload, message)
# 	 */
def update_password():
    server_url_update = "http://127.0.0.1:8000/update"
    taikhoan_update =input("input user need update :")
    password_update=input("input password need update :")
    # find value in tablecode and connet it into a string 
    found_values = find_value_by_string(password_update)

    if found_values:
        chuoi_value_kethop = ''.join(found_values)
        print(f"The entered password has been encoded into the table's string format : {chuoi_value_kethop}")
    else:
        print(f"No value found for string {password_update}")
    
    
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)
    print("this is default key :", fernet_key)

    matkhauki_mahoa = client_key.encrypt(chuoi_value_kethop.encode())
    matkhaugocguidi_hex = binascii.hexlify(matkhauki_mahoa).decode()
     # create a  dictionary sent to sever  . class InformationUser(BaseModel):/client_user: str/client_password: str 
    payload = {"taikhoannhap": taikhoan_update,"matkhaunhap": matkhaugocguidi_hex}
    # comand post send request to sever
    response = requests.post(server_url_update, json=payload)
if __name__ == "__main__":
    main()

    
