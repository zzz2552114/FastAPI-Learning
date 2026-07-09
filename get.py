from fastapi import FastAPI
from typing import Optional

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get('/greet/zhm')
async def greet_func():
    return "Nice to see you, ZHM"

@app.get('/books/{title}')
async def read_book(title):
    for item in BOOKS:
        if item.get('title').casefold() == title.casefold():
            return item
        else:
            return "NO SUCH BOOK"

@app.get('/books')
async def search_category(category:str):
        return [item for item in BOOKS if item.get('category').casefold( ) == category.casefold()] or "nothing found"
#   if result := [item for item in BOOKS if item.get('category').casefold( ) == category.casefold()]: 
#       return result
#   else:
#       return "nothing found"

@app.get('/books/query/{category}')
async def books_query(category:str, author:Optional[str] = "author one"):
    author_list = {book["author"].casefold() for book in BOOKS}
    category_list = {book["category"].casefold() for book in BOOKS}

    author_query = author in author_list
    category_query = category in category_list
    if not author_query and not category_query:
         return f"no author: {author} and no category: {category}"
    if not author_query:
         return f"no author: {author}"
    if not category_query:
         return f"no category: {category}"
    
    return [book for book in BOOKS if book['author'].casefold()==author and book['category'].casefold()==category] or f"author: {author} hasn't written any book about category: {category}"
    