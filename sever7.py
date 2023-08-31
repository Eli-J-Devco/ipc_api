from fastapi import FastAPI, HTTPException, Request
import os
import json
import datetime
import mysql.connector

app = FastAPI()

# Kết nối tới MySQL database
db=mysql.connector.Connect(user='root',password='123456',host='localhost')
# Tạo đối tượng con trỏ
mycursor = db.cursor()

@app.post("/receive_data/")
async def receive_data(request: Request):
    try:
        data = await request.json()  # Lấy dữ liệu JSON từ request body

        serialnumber = data.get("SERIALNUMBER", "")
        modbusport = data.get("MODBUSPORT", "")
        modbusdevice = data.get("MODBUSDEVICE", "")
        mode = data.get("MODE", "")
        password = data.get("PASSWORD", "")

        data_to_save = {
            "SERIALNUMBER": serialnumber,
            "MODBUSPORT": modbusport,
            "MODBUSDEVICE": modbusdevice,
            "MODE": mode,
            "PASSWORD": password
        }

        json_data = json.dumps(data_to_save, indent=4)  # Định dạng dữ liệu thành JSON

        # Lấy thời gian hiện tại để tạo tên file
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{current_time}.json"

        # Đường dẫn để lưu file
        file_path = os.path.join(r"D:\NEXTWWARE\VsCode\API\learnapi\DuyBinhLearnAPI\LuuData", file_name)

        # Lưu dữ liệu vào file JSON
        with open(file_path, "w") as f:
            f.write(json_data)

        # Lưu dữ liệu vào MySQL database
        db_cursor = db.cursor()
        sql_query = ("INSERT INTO `api`.`para`(`serialnumber`, `modbusport`, `modbusdevice`,`mode`,`password`,`json_file_path`) "
     + "VALUES (%s, %s, %s ,%s ,%s ,%s)")
        values  = [(serialnumber,modbusport,modbusdevice,mode,password,file_path)]
        db_cursor.execute(sql_query, values)
        db.commit()

        return {"message": f"File created, saved, and data inserted to MySQL successfully"} and print("serialnumber"+serialnumber,"modbusport"+modbusport,"modbusdevice"+modbusdevice,"mode"+mode,"passwword"+password,"json_file_path"+file_path)
                
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
