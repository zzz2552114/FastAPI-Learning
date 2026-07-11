from fastapi import FastAPI
# 第一步调包

app = FastAPI()
# 第二步创建实例(app) 这也是以后装饰器的前缀

@app.get('/greet/me')
async def greet_func():
    return "Nice to see you, my master ZHM"

@app.get('/greet/{name}')
async def greet_name_func(name:str):
    return f"Nice to see you, User {name}"

# 注意这里必须把写死的参数me放在路径参数函数/greet/{name}前面



# 下面拿一个实例讲一下查询参数和路径参数
BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]
## 下面这个是典型的路径参数
@app.get('/books/{title}')
async def read_book(title):
    for item in BOOKS:
        if item.get('title') == title:
            return item
    return "NOT FOUND SUCH BOOK"

## 然后是查询参数
@app.get('/books')
async def search_category(category:str):
    for i in BOOKS:
        if i.get('category',None) == category:
            return i
    return "NOT FOUND SUCH CATEGORY OF BOOK"

## 这里是路径参数和查询参数混合
@app.get('/books/q/{category}')
# 注意这里如果不加/q/会和第一个路径查询函数冲突！
# url就会变成/books/math?author=Author%20Five
# 在第一个路径里相当于查询title = math?author=Author%20Five
async def books_query(category:str, author:str | None = None ):
    result = []
    for i in BOOKS:
        if i.get('category') == category:
            if author == None :
               result.append(i)
            elif i.get('author') == author:
                result.append(i)
    if result:
        return result
    # 这里fastapi会自动把结果转换成json，json也可以是数组和普通字符串
    return "NOT FOUND SUCH BOOKLLLL"
