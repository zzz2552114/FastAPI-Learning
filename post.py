from fastapi import FastAPI,Body,Query,Form,File,UploadFile,Request
from pydantic import BaseModel,Field
from typing import *


app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

class BOOK_Mesagge(BaseModel):
    title:str=Field(...)
    author:str="Author One"

@app.post('/create_book')
async def create_book(cate_query:Literal["science","math"],post:BOOK_Mesagge):
    new_book = {}
    for book in BOOKS:
        if book.get('category').casefold() == cate_query.casefold():
            new_book = {'title' : post.title ,
                        'author' : post.author , 
                        'category' : cate_query
                        }

    BOOKS.append(new_book)
    return {
        "msg": "创建成功" if new_book else "创建失败",
        "data": new_book or "nothing",
        "current_total_books": len(BOOKS)
    }

@app.get('/book_database')
async def look_book_database():
    return BOOKS


class File_Message(BaseModel):
    filename:str=Field(...)
    filetype:str
    filesize_byte:int
class Request_Message(BaseModel):
    header:str
    cookie:dict
    method:Literal['GET','POST']

class Message(BaseModel):
    file_info: File_Message
    request_info: Request_Message

@app.post('/file')
async def post_file(file:UploadFile=File(),request:Request=None) -> Message:
    with open (file.filename,"wb") as f:
        while True:
            content = await file.read(1024*1024)
            if not content:
                break
            f.write(content)
    
    file_message = File_Message(
        filename = file.filename,
        filetype = file.content_type,
        filesize_byte = file.size           
    )
    head = str(request.headers)
    request_message = Request_Message(
        header = head,
        cookie = request.cookies,
        method = request.method
    )
    message = Message(
        file_info = file_message,
        request_info = request_message
    )
    print(file_message)
    print(request_message)
    print(message)
    await file.close()
    return message
