from fastapi import FastAPI,Cookie
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

@app.get("/items")
async def read_cookies(cook : Annotated[str|None,Cookie()] = None):
    return {"cookies":cook}

class cookies(BaseModel):
    name: str
    value: str
    session_id : str | None = None

@app.get("/items/c")
async def get_cookies(cookie:Annotated[cookies,Cookie()]):
    return {"cookies":cookie}