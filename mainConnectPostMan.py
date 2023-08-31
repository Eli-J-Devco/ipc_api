from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

app = FastAPI()
#-----------------------
#@app.get("/0")
# def TenHam():
#     return {"server yêu cầu đọc data có sẳn từ client"}
#-----------------------
#@app.post("/1")
# def TenHam():
#     return {"server yêu cầu client gửi dữ liệu mới lên "}
#------------------------
#@app.put("/2")
# def TenHam():
#     return {"server yêu cầu client update dữ liệu lại "}
#------------------------
#@app.delete("/3")
# def TenHam():
#     return {"server yêu cầu client xóa dữ liệu này "}

# uvicorn main:app --reload (code chạy server)
# http://127.0.0.1:8000/docs#/ (địa chỉ vào app )
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
async def delete_item(item_id:int):
    return {"item id":item_id}
