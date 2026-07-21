# 这一节讲的是在路径操作装饰器里的一些参数，主要是用于他人阅读
from enum import Enum

from fastapi import FastAPI

app = FastAPI()


class Tags(Enum):
    items = "items"
    users = "users"


@app.get("/items/", tags=[Tags.items])
async def get_items():
    return ["Portal gun", "Plumbus"]
# 这里tags表示标签，字符串形式，可以用Tags(Enum)类统一管理，但是没什么必要

@app.get('items/code',status_code=201)
async def items_status_code():
    return "OK"
# 响应码

@app.get('/items/ds',summary="it's a summary",description="this is a description for this path")
async def items_ds():
    return "good job"

@app.get('items/responce',response_description="Successfuly send a responses")
async def res(item:str):
    return {"item" : item}
