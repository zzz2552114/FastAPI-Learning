'''
UUID:
一种标准的 "通用唯一标识符" ，在许多数据库和系统中用作ID。
在请求和响应中将以 str 表示。
datetime.datetime:
一个 Python datetime.datetime.
在请求和响应中将表示为 ISO 8601 格式的 str ，比如: 2008-09-15T15:53:00+05:00.
datetime.date:
Python datetime.date.
在请求和响应中将表示为 ISO 8601 格式的 str ，比如: 2008-09-15.
datetime.time:
一个 Python datetime.time.
在请求和响应中将表示为 ISO 8601 格式的 str ，比如: 14:23:55.003.
datetime.timedelta:
一个 Python datetime.timedelta.
在请求和响应中将表示为 float 代表总秒数。
Pydantic 也允许将其表示为 "ISO 8601 时间差异编码", 查看文档了解更多信息。
frozenset:
在请求和响应中，作为 set 对待：
在请求中，列表将被读取，消除重复，并将其转换为一个 set。
在响应中 set 将被转换为 list 。
产生的模式将指定那些 set 的值是唯一的 (使用 JSON Schema 的 uniqueItems)。
bytes:
标准的 Python bytes。
在请求和响应中被当作 str 处理。
生成的模式将指定这个 str 是 binary "格式"。
Decimal:
标准的 Python Decimal。
在请求和响应中被当做 float 一样处理。

实在不行就去pydantic官网查
https://pydantic.dev/docs/validation/latest/concepts/models/
'''