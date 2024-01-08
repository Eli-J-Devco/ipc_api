import requests
from fastapi import FastAPI

app = FastAPI()

@app.post("/send_data")
async def receive_data(data: dict):  # Thay đổi kiểu dữ liệu thành dict
    print(f"Received data: {data}")
    return {"status": "success", "message": "Data received successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    
# câu lênh chạy file sever : uvicorn Sever:app --reload