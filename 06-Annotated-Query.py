from fastapi import FastAPI,Query
from typing import Annotated
from pydantic import BaseModel,Field

app = FastAPI()

@app.get("/items/q1")
async def query_items(q:Annotated[str | None, Query(...,max_length=20)] = None):
    if q:
        return {"items" : q}
    return "NOT FOUND"


@app.get("/annother_items/")
async def read_items(q: Annotated[list[str], Query(alias="qry")] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items
# 这个例子说明查询参数可以是列表
# !!!!Annotated里面也可以用AfterValidator自定义检验器，return id而不是bool值

class filter_query(BaseModel):
    model_config = {"extra":"forbid"}
    id: int = Field(ge=1,lt=100)
    title: str = Field(min_length=1,max_length=20)
    category: str | None = None
    price: float

@app.get("/items/q2/")
async def Filter_Q(qry:Annotated[filter_query,Query()]):
    return  qry