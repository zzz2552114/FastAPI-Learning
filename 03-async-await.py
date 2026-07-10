import asyncio


async def db_query():
    pass
def dq():
    pass
async def a():
    data = await db_query()   # 挂起
    # 注意这里db_query必须是异步的，如果是同步的就会报错，所以数据库要用异步库

    # 或者用异步函数装饰一下，背过这个东西，asyncio.to_thread
    data1 = await asyncio.to_thread(dq())
    return data,data1

