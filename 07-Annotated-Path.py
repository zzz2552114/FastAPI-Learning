from fastapi import FastAPI,Path,Query
from typing import Annotated

app = FastAPI()

@app.get("/items/{item_id}")
async def read_items(
        item_id:Annotated[int, Path(description="Item id to get",gt=0)],
        # Path用来操作路径参数，和Query对于查询参数来说一样
        q:Annotated[str | None, Query(title="Query id to get")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results