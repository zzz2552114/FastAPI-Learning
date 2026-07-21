from fastapi import FastAPI
from pydantic import BaseModel,EmailStr

app = FastAPI()
class Item1(BaseModel):
    item_id: int
    name: str
    price: float = 1.0
@app.get("/items")
async def get_item(item : Item1) -> Item1:
    return item
# 这里表示，可以用 -> 来指明返回类型
# 首先要注意一点：在 FastAPI 里，给路径操作函数写上 -> 返回类型，和普通 Python 函数有本质区别。FastAPI 会强制进行校验。

# 但是有的时候没那么好用，比如看下面的例子
class UserInput(BaseModel):
    username: str
    email: EmailStr = "xxx@example.com"
    password: str
class UserOutput(BaseModel):
    username: str
    email: EmailStr
# 这两个类表示，用户输入的时候需要输入密码，但是为了安全，返回给用户信息的时候不能包含密码
# 那么下面这么写就不行了
# @app.get("/register")
# async def register_user(user_in: UserInput) -> UserOutput:
#     return user_in
# 响应类型注解会出现矛盾，但是如果改成response_model的话，就没问题了，fastapi会自动转换
@app.get("/register",response_model=UserOutput)
async def register_user(user_in: UserInput):
    return user_in
# 但是此时问题在于：我们无法从编辑器处获得对函数返回类型的检查支持

# 另一种解决思路是用继承类，但是只是针对这种特殊情况好用

class BaseInput(BaseModel):
    username: str
    email: EmailStr
class UserIn(BaseInput):
    password: str
@app.post("/login")
async def login_user(user_in: UserIn) -> BaseInput:
    return user_in
# 用继承类就可以做到转化了

# 还要注意一点，如果->类型注解后是类似于 Response | dict 的内容，会校验失败


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]
# 这个例子说明了，response_model_exclude_unset=True的用法。在响应体里，会忽略掉没有设置的、有默认值的值

# 你还可以使用路径操作装饰器的 response_model_include 和 response_model_exclude 参数。
# 它们接收一个由属性名组成的 set，用于！！！包含（忽略其他）或排除（包含其他）！！！这些属性

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]
# 这里只会返回name和description两个属性

@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]
# 这里除了tax属性其他的都会返回

## 但是其实fastapi官方不推荐这种做法。他们很看重Swagger UI的文档生成和文档说明
# 这种response_model，以及include/exclude/exclude_unset都不会在自动文档中显示。
# 他们更推荐多弄几个类，正儿八经地类型校验。


# 下面再来研读一个例子

class User1Base(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class User1In(User1Base):
    password: str


class User1Out(User1Base):
    pass


class User1InDB(User1Base):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password
# 这是加密示例

def fake_save_user(user_in: User1In):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = User1InDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db
'''这里的意思是:
获取一个User1In，里面有明文密码。
先加密，然后解包+传参，变成User1InDB这个模型，里面会自动忽略明文密码
'''

@app.post("/user/", response_model=User1Out)
async def create_user(user_in: User1In):
    user_saved = fake_save_user(user_in)
    return user_saved
# 这里是，先获取User1InDB这个数据模型，在返回的时候用response_model转换成User1Out模型，丢弃哈希后的密码

# 最后一点需要注意的是，response_model后面如果要传联合类型，不能用 | ，必须用typing库里的Union！！！
# 因为response_model相当于参数而不是类型注解
