from fastapi import FastAPI
from typing import Annotated
from pydantic import Field
import os
import aiofiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
curr_path = os.path.dirname(__file__)
post_path = os.path.join(curr_path, "post")

@app.get("/posts")
async def list_posts():
    postnames = []
    try:
        for i in os.listdir(post_path):
            if i.endswith(".md"):
                name = os.path.splitext(os.path.basename(i))[0]
                postnames.append(name)
    except FileNotFoundError or NotADirectoryError:
        return {"posts":[]}
    return {"posts": postnames}

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    file_path = os.path.join(post_path, f'{post_id}.md')
    try:
        async with aiofiles.open(file_path, "r", encoding='utf-8') as f:
            content = await f.read()
    except FileNotFoundError:
        return {"error": "post not found"}
    except Exception as e:
        return {"error": f"failed to read : {str(e)}"}
    return {"id": post_id,"content": content}
