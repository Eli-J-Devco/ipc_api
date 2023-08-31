import mysql.connector
db=mysql.connector.Connect(user='root',password='123456',host='localhost')

# Tạo đối tượng con trỏ
mycursor = db.cursor()

# Câu truy vấn INSERT
# code9 =  ("INSERT INTO `api`.`para`(`serialnumber`, `modbusport`, `modbusdevice`,`mode`,`password`,`json_file_path`) " + "VALUES (%s, %s, %s, %s, %s, %s)")
# #giá trị của một row được cung cấp dưới dạng tuple
# val = (1, 2, 3, 4, 5, 6)

code9 = ("INSERT INTO `api`.`para`(`serialnumber`, `modbusport`, `modbusdevice`,`mode`,`password`,`json_file_path`) "
     + "VALUES (%s, %s, %s ,%s ,%s ,%s)")

#giá trị của một row được cung cấp dưới dạng tuple
serialnumber = input("serialnumber")
modbusport = input("MODBUSPORT")
modbusdevice = input("MODBUSDEVICE")
mode = input("MODE")
password = input("PASSWORD")
json_file_path = input("json_file_path")

val = [(serialnumber,modbusport,modbusdevice,mode,password,json_file_path)]

# Thực hiện truy vấn SELECT,truy vấn nào thì chọn code đó. 
try:
    mycursor.executemany(code9,val)
 
    #commit the transaction
    db.commit()
 
except:
   db.rollback()
 
print("record inserted!")
mycursor.close()