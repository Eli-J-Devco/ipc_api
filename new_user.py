# /********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/ 
import mysql.connector
import bcrypt

db=mysql.connector.Connect(user='root',password='123456',host='localhost')

# Tạo đối tượng con trỏ
mycursor = db.cursor()

# Câu truy vấn INSERT
code9 = ("INSERT INTO `login`.`data`(`ID`, `user`, `password`) "
    + "VALUES (%s, %s, %s)")

#giá trị của một row được cung cấp dưới dạng tuple
ID =int(input("Thêm data vào cột ID :"))
tk =input("Thêm data vào cột user :")
mk =input("Thêm data vào cột password : ")

# Mã hóa mật khẩu
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(mk.encode(), salt)
print(hashed_password)

val = (ID, tk, hashed_password)

# Thực hiện truy vấn SELECT,truy vấn nào thì chọn code đó. 
try:
    mycursor.execute(code9,val)
 
    #commit the transaction
    db.commit()
 
except:
   db.rollback()
 
print("record inserted!")
mycursor.close()