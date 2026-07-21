from fastapi import FastAPI,Header
from typing import Annotated
from pydantic import BaseModel,Field

app = FastAPI()

@app.get("/items/")
async def get_items1(header : Annotated[str|None,Header()] = None):
    return header

class HeaderClass(BaseModel):
    host : str = Field(...,min_length=5)
    user_agent : str = Field(default="gugugaga")
@app.get("/items/h")
async def get_items(header : Annotated[HeaderClass,Header()]):
    return header
