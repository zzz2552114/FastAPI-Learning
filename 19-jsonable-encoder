from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
# 记住这个库
from pydantic import BaseModel

fake_db = {}

class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    # 这里的这个jsonable_encoder，可以把pydantic模型转换成dict，内部的datatime类型转换成str，转换后可以兼容JSON
    fake_db[id] = json_compatible_item_data
