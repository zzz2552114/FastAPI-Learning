from fastapi import FastAPI,status

app = FastAPI()


@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}

@app.get("/items/another", status_code=status.HTTP_201_CREATED) # 这个可以让编辑器给提示
async def get_item(name: str):
    return {"name": name}
'''
100 - 199 用于返回“信息”。这类状态码很少直接使用。具有这些状态码的响应不能包含响应体
200 - 299 用于表示“成功”。这些状态码是最常用的
200 是默认状态码，表示一切“OK”
201 表示“已创建”，通常在数据库中创建新记录后使用
204 是一种特殊的例子，表示“无内容”。该响应在没有为客户端返回内容时使用，因此，该响应不能包含响应体
300 - 399 用于“重定向”。具有这些状态码的响应不一定包含响应体，但 304“未修改”是个例外，该响应不得包含响应体
400 - 499 用于表示“客户端错误”。这些可能是第二常用的类型
404，用于“未找到”响应
对于来自客户端的一般错误，可以只使用 400
500 - 599 用于表示服务器端错误。几乎永远不会直接使用这些状态码。应用代码或服务器出现问题时，会自动返回这些状态码
'''