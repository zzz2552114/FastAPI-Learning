from unittest.mock import Base

from anyio import Path
from fastapi import Depends, FastAPI, Query
from typing import Annotated,Any
from pydantic import Field,BaseModel
from pathlib import Path as pPath
import aiofiles
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/v1/health')
async def health_check():
    return {"project" : "Blog" ,
            "status" : "ok"}

class postbasic(BaseModel):
    id : int = Field(...,ge=1)
    title : str
    author : str = "zhm"

class postlink(postbasic):
    link :str

class postcontent(postbasic):
    content : Any

post_path = r"E:\learn-fastapi\Blog-Project\backend\post"
post_info_path = pPath(post_path)/"posts-info.txt"

items : list[postlink] = []

@app.get("/api/v1/posts")
def list_posts():
    global items
    items  = []
    cnt = 0
    try:
        with open(post_info_path,'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    line = json.loads(line) # 这一步把line转换成字典
                    items.append(postlink.model_validate(line))
                    cnt += 1
    except FileNotFoundError as e:
        return {"error": "post directory not found"}
    return {"items": items,"total": cnt}

async def find_post_by_id(post_id):
    for item in items:
        if post_id == str(item.id): 
            file_path = pPath(post_path)/f'{item.link}'
            try:
                async with aiofiles.open(file_path, "r", encoding='utf-8') as f:
                    content = await f.read()
            except FileNotFoundError:
                return {"error": "post not found"}
            except Exception as e:
                return {"error": f"failed to read : {str(e)}"}
            finally:
                break
    return {
        "id": post_id,
        "title": item.title,
        "author": item.author,
        "content": content
        }
     

@app.get("/api/v1/posts/{post_id}/related")
async def list_related_posts(post_id:str):
    curr_post = await find_post_by_id(post_id)
    author = curr_post['author']
    result : list[postcontent] = []
    for item in items:
        if post_id == str(item.id):
            continue
        if author == item.author:
            result.append(postcontent(**item.model_dump(),content = item.link))
    if result:
        return result
    return f"没有找到作者{author}的相关帖子"

@app.get("/api/v1/posts/latest")
async def get_latest_post():
    latest_post = max(items, key=lambda x: x.id)
    id = str(latest_post.id)
    return id

@app.get("/api/v1/posts/{post_id}")
async def get_post_detail(post_id: str):
    result = await find_post_by_id(post_id)
    return result

class PostCreate(BaseModel):
    title : str
    author : str = "zhm"
    content : str

def generate_post_id():
    if not items:
        return 1
    return max(item.id for item in items) + 1

@app.post('/api/v1/posts')
async def create_post(post : PostCreate):
    title = post.title.strip()
    author = post.author.strip()
    content = post.content.strip()
    if not title or not content:
        return {"error": "title and content cannot be empty"}
    new_id = generate_post_id()
    new_post = {
        "id": new_id,
        "title": title,
        "author": author,
        "link": f"{new_id}.md"
    }
    items.append(postlink.model_validate(new_post))
    post_file_path = pPath(post_path)/f"{new_id}.md"
    try:
        async with aiofiles.open(post_file_path, "w", encoding='utf-8') as f:
            await f.write(content)
        async with aiofiles.open(post_info_path, "a", encoding='utf-8') as f:
            await f.write(json.dumps(new_post) + "\n")
    except Exception as e:
        return {"error": f"failed to save post: {str(e)}"}  
    return {"message": "post created successfully", "post": new_post}


@app.post('/api/v1/posts/preview')
async def preview_post(post: PostCreate):
    content = post.content.strip()
    if not content:
        return {"error": "content cannot be empty"}
    # 统计字数和行数
    word_count = 0
    line_count = 1
    for i in range(len(content)):
        if content[i] == '\n':
            line_count += 1
        if content[i].isspace():
            continue
        word_count += 1
    # 计算阅读时间
    time = max(1, word_count // 500)  # 假设平均阅读速度为每分钟300字
    post_preview = {
        "title": post.title,
        "author": post.author,
        "line_count": line_count,
        "word_count": word_count,
        "time": time
    }
    return post_preview

class PostQuery(Base):
    keyword : str | None = None
    skip : int = Field(default=0, ge=0)
    limit : int = Field(default=5, ge=1, le=100)

@app.get('/api/v1/posts/search')
async def search_posts(
    post: PostQuery = Depends()):
        keyword = post.keyword
        skip = post.skip
        limit = post.limit
        if keyword:
            keyword = keyword.casefold().strip()
        result = []
        for item in items:
            if keyword and keyword.lower() not in item.title.lower():
                continue
            result.append(item)
        total = len(result)
        paginated = result[skip:skip + limit]
        return {
            "items": paginated,
            "total": total,
            "skip": skip,
            "limit": limit
        }
