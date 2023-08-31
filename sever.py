#gửi api +file lên server thì server return lại json data báo gửi thành công, client sẽ gửi file tiếp theo.
#Data gửi lên tuần tự từng file
#Em viết code tạo file đó, có thể  lưu đường dẫn , thống tin file, nội dung file Trên MySQL
#Nội dung file đó:
#'2023-08-15 10:35:04',0,0,0,50,23,55
#các giá trị random. 5p tạo 1 file, để nhanh thì 5s tạo file 1 lần. sau này hệ thống log 5p

#uvicorn sever:app --reload

from fastapi import FastAPI, Form
import os
import json

app = FastAPI()

@app.post("/receive_data/")
async def receive_data(data: dict):
    try:
        # Chuyển dữ liệu thành chuỗi JSON
        json_data = json.dumps(data)

        # Tạo file dưới định dạng .json
        file_path = os.path.join(r"C:\Users\HP\Desktop\CaNhan\API\learnapi\DuyBinhLearnAPI\LuuData", f"{data['key']}.json")
        with open(file_path, "w") as f:
            f.write(json_data)

        return {"message": f"File '{data['key']}.json' created and saved successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    # kết nối thành công giữa client và sever 
    





