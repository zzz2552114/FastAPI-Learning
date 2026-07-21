from fastapi import FastAPI,Form,UploadFile
from pydantic import BaseModel
from typing import Annotated

# 首先，建议先看16-的两个.md文件，里面很清晰地讲了Form和UploadFile的原理

#注意，这一部分是客户端提交内容，所以是post方法

app = FastAPI()
@app.post("/form1")
async def form1(form : Annotated[str, Form(...)]):
    return form
# 这是第一种写法，注意Form不是一种数据类型，而是一个声明函数，返回一个类对象

class FormData(BaseModel):
    username: str
    password: str
@app.post("/form2")
async def form2(form : Annotated[FormData, Form(...)]):
    return form

# 这基本上就是纯Form的两种用法
# 在这里，Form的主要用处就是提供一个与JSON不同的请求体
# 下面会讲Form的另外一个用处，它的子类，File。用于上传文件
# 然后还要介绍一种接收文件的数据类型，叫UploadFile
@app.post("/form3")
async def form3(form : Annotated[FormData, Form(...)]):
    return form
'''
UploadFile 的属性如下：UploadFile.xxx
    filename：上传的原始文件名字符串（str），例如 myimage.jpg。
    content_type：内容类型（MIME 类型 / 媒体类型）的字符串（str），例如 image/jpeg。
    file：返回一个文件对象，相当于python同步版本的一个文件，有各种相同的操作
    
下面是一些方法：都是异步的，要加await！！！
    write(data)：将 data (str 或 bytes) 写入文件。
    read(size)：读取文件中 size (int) 个字节/字符。
    seek(offset)：移动到文件中字节位置 offset (int)。
    close()：关闭文件。

例如，在 async 路径操作函数 内，你可以这样获取内容：
contents = await myfile.read()

如果是在普通 def 路径操作函数 内，你可以直接访问 UploadFile.file，变成异步
contents = myfile.file.read()
'''

# 多文件上传可以用list[UploadFile]
""" 前端可以这么写
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
"""
