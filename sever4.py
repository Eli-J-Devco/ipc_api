from fastapi import FastAPI, HTTPException, Request
import os
import json
import datetime

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

        # Lấy thời gian hiện tại để tạo tên file
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{current_time}.json"

        # Đường dẫn để lưu file
        file_path = os.path.join(r"C:\Users\HP\Desktop\CaNhan\API\learnapi\DuyBinhLearnAPI\LuuData", file_name)

        # Lưu dữ liệu vào file JSON
        with open(file_path, "w") as f:
            f.write(json_data)

        return {"message": f"File '{file_name}' created and saved successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    # gửi thành công file từ client lên sever và lưu vào đường dẫn dưới tên file là ngày tháng năm . 
