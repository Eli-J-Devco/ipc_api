# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 
import mysql.connector
import bcrypt
from cryptography.fernet import Fernet
import binascii

db=mysql.connector.Connect(user='root',password='123456',host='localhost')

# Tạo đối tượng con trỏ
mycursor = db.cursor()

#giá trị của một row được cung cấp dưới dạng tuple
tk =input("Thêm data vào cột user :")
mk =input("Thêm data vào cột password : ")

# Select coi đã có người dùng hay chưa 
code8 = ("SELECT user FROM login.data WHERE user = %s")
val1 = (tk,)
# Thực hiện truy vấn SELECT,truy vấn nào thì chọn code đó. 
try:
    mycursor.execute(code8,val1)
 
    #commit the transaction
    db.commit()
 
except:
   db.rollback()
result = mycursor.fetchall()
if result:
    tupleuser = result[0]
    user = tupleuser[0]
    if user == tk :
        print("user đã tồn tại .")
    else:
        print("user chưa tồn tại")
# Câu truy vấn INSERT
code9 = ("INSERT INTO `login`.`data`(`user`, `password`, `salt`) "
    + "VALUES ( %s, %s,%s)")

# Mã hóa mật khẩu
salt = bcrypt.gensalt()
print("mã salt đúng là :", salt)
salt_hex = binascii.hexlify(salt).decode()
print("mã salt chuyển sang hex là :", salt_hex)
hashed_password = bcrypt.hashpw(mk.encode(), salt)
print(" Mật khẩu băm qua bcrypt", hashed_password)
hashed_password_hex = binascii.hexlify(hashed_password).decode()
print("mật khẩu bcrypt chuyển sang hex là :", hashed_password_hex)

val2 = ( tk, hashed_password_hex,salt_hex)

# Thực hiện truy vấn SELECT,truy vấn nào thì chọn code đó. 
try:
    mycursor.execute(code9,val2)
 
    #commit the transaction
    db.commit()
 
except:
   db.rollback()
 
print("record inserted!")
mycursor.close()