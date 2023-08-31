from fastapi import FastAPI, Form
import os
import json
#uvicorn sever7:app --reload
app = FastAPI()

@app.post("/receive_data/")
async def receive_data(data: dict):
    try:
        # Tạo tên file dựa trên dữ liệu
        file_name = f"{data['key']}.json"
        
        # Chuyển dữ liệu thành chuỗi JSON
        json_data = json.dumps(data)

        # Tạo file dưới định dạng .json
        file_path = os.path.join(r"C:\Users\HP\Desktop\CaNhan\API\learnapi\DuyBinhLearnAPI\LuuData", file_name)
        with open(file_path, "w") as f:
            f.write(json_data)

        return {"message": f"File '{file_name}' created and saved successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    #đọc data từ client lên rồi chuyển thành file json 