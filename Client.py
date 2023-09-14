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
    print("""
    1 - user_settings()
    2 - data_record ()
    3 - config_device()
    4 - control_device()
    """)
    choosemain_menu = int(input("Command: "))

    if choosemain_menu == 1 :
        user_settings()
    elif choosemain_menu == 2 :
        data_record()
    elif choosemain_menu == 3 :
        config_device()
    elif choosemain_menu == 4 :
        control_device() 
    else :
        print("Lựa chọn không hợp lệ")
        
def data_record():
    return
def config_device():
    return
def control_device():
    return
def user_settings():
    choose_user = int(input("Chọn 0 để đăng kí hoặc 1 để đăng nhập: "))

    if choose_user == 0:
        dangki()
    elif choose_user == 1:
        dangnhap()
    else:
        print("Lựa chọn không hợp lệ")

def dangnhap():

    # Thay đổi URL thành URL thực tế của server
    server_url_dangnhap = "http://127.0.0.1:8000/login"

    # gửi thông tin tài khoản , mật khẩu , mật khẩu salt , mật khẩu fernet . 
    #giá trị của một row được cung cấp dưới dạng tuple
    taikhoannhap= input("Nhập tài khoản đăng nhập:")
    matkhaunhap = input("Nhập mật khẩu đăng nhập:")

    # Tìm giá trị tương ứng và nối chúng thành một chuỗi
    found_values = find_value_by_string(matkhaunhap)

    if found_values:
        chuoi_value_kethop = ''.join(found_values)
        print(f"Mật khẩu nhập vào đã mã hóa sang kiểu chuổi của bảng : {chuoi_value_kethop}")
    else:
        print(f"Không tìm thấy giá trị nào cho chuỗi {matkhaunhap}")
    
    
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)
    print("Đây là khóa mặc định :", fernet_key)

    # Mã hóa mật khẩu bcrypt với khóa Fernet
    matkhauki_mahoa = client_key.encrypt(chuoi_value_kethop.encode())
    # print("Mật khẩu đã được mã hóa:", matkhauki_mahoa.decode())
    matkhaugocguidi_hex = binascii.hexlify(matkhauki_mahoa).decode()
    # print("thông tin gửi đi gồm :", matkhaugocguidi_hex)
    # Tạo một dictionary chứa giá trị input // payload này tên như thế nào thì class InformationUser(BaseModel):/client_user: str/client_password: str tên như thế mới kết nối được 
    payload = {"taikhoannhap": taikhoannhap,"matkhaunhap": matkhaugocguidi_hex}

    #client_key_hex => mã hóa lại byte => client_key = Fernet(fernet_key) để lấy key thật 

    # Gửi yêu cầu POST đến server FastAPI với dữ liệu JSON
    response = requests.post(server_url_dangnhap, json=payload)

def dangki():
    # Thay đổi URL thành URL thực tế của server
    server_url_dangki = "http://127.0.0.1:8000/register"
    taikhoanki =input("Đăng kí tên tài khoản mới :")
    matkhauki =input("Đăng kí mật khẩu mới : ")
     # Tìm giá trị tương ứng và nối chúng thành một chuỗi
    found_values = find_value_by_string(matkhauki)

    if found_values:
        chuoi_value_kethop = ''.join(found_values)
        print(f"Mật khẩu nhập vào đã mã hóa sang kiểu chuổi của bảng : {chuoi_value_kethop}")
    else:
        print(f"Không tìm thấy giá trị nào cho chuỗi {matkhauki}")
    # mã hóa thông tin qua 2 lớp
    # mật khẩu cố định cho cho Fernet
    # Tạo một khóa Fernet mặc định 
    fernet_key = b'PjWEC41lNvBaTXZaQoSGwSA_tt9RD-D4cZMWn06R1H4='
    client_key = Fernet(fernet_key)
    print("Đây là khóa mặc định :", fernet_key)

    # Mã hóa mật khẩu bcrypt với khóa Fernet
    matkhauki_mahoa = client_key.encrypt(chuoi_value_kethop.encode())
    print("Mật khẩu đã được mã hóa:", matkhauki_mahoa)
    matkhaugocguidi_hex = binascii.hexlify(matkhauki_mahoa).decode()
    print("thông tin gửi đi gồm :", matkhaugocguidi_hex)

    # Tạo một dictionary chứa giá trị input // payload này tên như thế nào thì class InformationUser(BaseModel):/client_user: str/client_password: str tên như thế mới kết nối được 
    payload = {"taikhoannhap": taikhoanki,"matkhaunhap": matkhaugocguidi_hex}
    #client_key_hex => mã hóa lại byte => client_key = Fernet(fernet_key) để lấy key thật 

    # Gửi yêu cầu POST đến server FastAPI với dữ liệu JSON
    response = requests.post(server_url_dangki, json=payload)

    #gửi thông tin tài khoản và mật khẩu 
    #Giá trị input bạn muốn gửi lên server


if __name__ == "__main__":
    main()

    
