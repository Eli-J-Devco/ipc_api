from fastapi import FastAPI, HTTPException, Request
import os
import json
import uuid

app = FastAPI()

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

        # Tạo tên file dựa trên chuỗi ngẫu nhiên
        file_name = f"{str(uuid.uuid4())}.json"

        # Đường dẫn để lưu file
        file_path = os.path.join(r"C:\Users\HP\Desktop\CaNhan\API\learnapi\DuyBinhLearnAPI\LuuData", file_name)

        # Lưu dữ liệu vào file JSON
        with open(file_path, "w") as f:
            f.write(json_data)

        return {"message": f"File '{file_name}' created and saved successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    # đã tạo thành công sever đọc file từ client và lưu từng file vào đường dẫn 
