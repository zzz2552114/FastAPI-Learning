from fastapi import FastAPI,Body,Query,Form,File,UploadFile,Request
from pydantic import BaseModel,Field
from typing import Annotated
from enum import  Enum


app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

class categoryEnum(str, Enum):
    Science = "science"
    Math = "math"
    History = "history"

class BOOK_Message(BaseModel):
    title:str=Field(...)
    """ 这里解释一下Field。
    Field可以让我们对请求体进行一些约束，保证我们收到的信息是符合格式的
    Field里面的几个参数：
    ...表示该选项必填，如果不是...而是某个值，则为默认值
    min_length/max_length限制str长度，pattern正则验证
    gt,le限制数值范围
    description，example是接口文档标注，开发时交流使用
    """
    author:str=Field("Author One")

@app.post('/create_book')
# 注意下面的用法：Annotated是业界推荐!!!而不是和上面的Field一个用法
async def create_book(cate_query:categoryEnum, post:BOOK_Message=Body(...)):
    new_book = {}
    for book in BOOKS:
        if book.get('category').casefold() == cate_query.casefold():
            new_book = {'title' : post.title ,
                        'author' : post.author , 
                        'category' : cate_query
                        }
    # 这个例子同时练习到了查询参数和请求体。只能根据已有种类新建书籍
    BOOKS.append(new_book)
    return {
        "msg": "创建成功" if new_book else "创建失败",
        "data": new_book or "nothing",
        "current_total_books": len(BOOKS)
    }

@app.get('/book_database')
async def look_book_database():
    return BOOKS


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    # 这里item_id是路径参数，q是查询参数，item是请求体。fastapi自动识别
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
