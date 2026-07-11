from fastapi import FastAPI,Body,Query
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel): # 第一个请求体
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel): # 第二个请求体
    username: str
    full_name: str | None = None


@app.put("/items/{item_id}")
async def update_item(
    item_id: int, # 路径参数
    item: Item, # body1
    user: User, # body2
    importance: Annotated[int, Body(gt=0)], # body3
    q: str | None = None, # 查询参数
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results

"""有一个挺有意思的点，不知道以后有没有用
假如只有一个请求体，那么会解析一个多键值对的object
比如
{
    "name": "aaa",
    "description": "bbb",
    "price": 100.0,
    "tax": 66.6 
}
但是如果有多个请求体，就会把请求体参数的名字加进来当作键，任何它的值就是上面的object
例如
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    },
    "importance": 5
}
当然了如果单个请求体想要有这样的效果也可以，body(embid=True)
"""