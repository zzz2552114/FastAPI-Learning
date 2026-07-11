from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

# 注意这里HttpUrl会校验一个如下类似的字符串
# "http://example.com/baz.jpg"

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None # 第一层嵌套
    # list和set一样常用，set哈希表不允许重复，且初始化空集合要set()
''' 关于images的键值对就像下面这样，键是名字，值是列表
{ 
"images": [
        {
            "url": "http://example.com/baz.jpg",
            "name": "The Foo live"
        },
        {
            "url": "http://example.com/dave.jpg",
            "name": "The Baz"
        }
    ]
}
'''

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]
''' 那么同理这里的items应该是什么呢？
键："items"
值是一个列表，里面的每个元素都是花括号，花括号里的键值对是Item声明的东西
其中images的值依旧是列表，如上面所示
'''


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer




@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images
# 这样也可以，这样获取到的JSON就不是object形式。而直接是列表形式