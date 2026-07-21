# FastAPI × 原生 JavaScript × Vue 3 双主线前后端并行学习手册
## ——从第一个阶段开始真实 `fetch`，逐路由、逐函数、逐逻辑、逐返回值与逐页面交互完全详解版

> 适用读者：Python 较熟练，算法基础较好；JavaScript 只熟悉变量、数组、对象、函数、DOM、事件和基础 `fetch`。
>
> 双主线项目：**个人博客系统**、**事件竞猜与预测市场（只使用虚拟积分，不涉及真实资金）**。
>
> 本手册不提供整套可复制代码，但会提供足够具体的函数职责、输入、处理步骤、示例数据、返回值、错误情况和前后端交互说明。你需要亲手写代码，但不会再被一句“实现分页”“处理搜索”丢在半路。
>
> 文档核对日期：2026-07-16。

---

# 1. 前后端通信全过程

假设浏览器要获取文章列表。

## 1.1 用户做了什么

用户打开博客页面，或者点击“刷新文章”按钮。

## 1.2 JavaScript 做了什么

JavaScript 调用：

```text
fetch("http://127.0.0.1:8000/api/v1/posts")
```

这句话的含义不是“直接拿到文章数组”，而是“开始向这个 URL 发 HTTP 请求”。

## 1.3 后端做了什么

FastAPI 根据请求方法和路径寻找匹配路由：

```text
GET /api/v1/posts
```

匹配后，FastAPI 调用你写的 `list_posts` 路由函数。

## 1.4 路由函数做了什么

`list_posts` 从当前的数据存储中取得文章，整理出准备公开给前端的字段，然后返回 Python 字典或列表。

FastAPI 会把 Python 数据转换成 JSON 响应。

## 1.5 浏览器收到了什么

浏览器先得到一个 `Response` 对象。它包含：

- 状态码，例如 200、404、422；
- 响应头；
- 响应体。

`fetch` 在收到 404 时通常也会正常得到 `Response`，不会自动进入 `catch`。所以必须检查 `response.ok`。

## 1.6 `response.json()` 做了什么

后端返回的是 JSON 文本。`await response.json()` 会解析它，得到普通 JavaScript 对象。

例如后端响应：

```json
{
  "items": [
    {"id": 1, "title": "第一篇文章", "author": "Hazel"}
  ],
  "total": 1
}
```

前端解析后可以访问：

```text
data.items
data.total
data.items[0].title
```

## 1.7 DOM 为什么要在拿到数据后更新

后端 JSON 本身不会自动显示到页面。JavaScript 必须：

1. 清空原来的文章按钮；
2. 遍历 `data.items`；
3. 为每篇文章创建一个按钮；
4. 把按钮文字设为文章标题；
5. 点击按钮时，再请求对应详情；
6. 把详情写入标题和正文元素。

这就是完整的“前端调用后端”链路。

---

# 2. 统一项目目录

```text
fastapi-fullstack-lab/
├── README.md
├── blog-system/
│   ├── backend/
│   │   └── app/
│   │       └── main.py
│   └── frontend/
│       ├── index.html
│       └── scripts/
│           └── main.js
└── prediction-market/
    ├── backend/
    │   └── app/
    │       └── main.py
    └── frontend/
        ├── index.html
        └── scripts/
            └── main.js
```

每个阶段继续修改同一套目录。阶段版本使用 Git commit/tag 保存，不复制 `phase1`、`phase2` 文件夹。

## 2.1 本地运行方式

后端目录中运行 FastAPI，例如使用 8000 端口。

前端目录中运行：

```text
python -m http.server 5500
```

然后访问：

```text
http://127.0.0.1:5500
```

不要直接双击 `index.html`。通过 HTTP 服务器打开，更接近真实网站，也方便 CORS 与后续模块加载。

你一次只运行一个项目，因此博客和预测市场都固定使用后端 `8000`、前端 `5500`。切换项目时，先停止当前项目的两个进程，再启动另一个项目。

---

# 3. 官方学习阶段总览

> 学习顺序仍以 FastAPI 官方章节为主。唯一有意提前使用的是“最小 CORS 桥接配置”，因为你明确要求前后端从第一天并行。阶段 0 只照着配置并理解“允许哪个前端地址”，到阶段 7 再系统学习预检、credentials、允许头和暴露响应头。

| 阶段 | 进入阶段前应学习的官方内容 | 后端真实增量 | 同阶段前端真实增量 |
|---|---|---|---|
| 0 | 第一步 | `/health` | `fetch /health` 显示连接状态 |
| 1 | 路径参数、最基础查询参数 | 文章/事件列表与详情 | 真实加载按钮与详情 |
| 2 | 请求体、Body/Field、基础模型 | 创建文章、创建事件、下注 | 真实表单 POST |
| 3 | 查询校验、查询模型、响应模型、状态码 | keyword、skip、limit、稳定列表响应 | 搜索、上一页、下一页 |
| 4 | Form、File、错误处理、更新数据 | PATCH、DELETE、Markdown 上传、事件关闭/取消 | 编辑、删除、FormData 上传、状态按钮 |
| 5 | 依赖项全部章节 | 复用分页、查资源、开放状态等前置条件 | 原有页面继续真实联调并观察错误 |
| 6 | 安全性全部章节 | 密码哈希、OAuth2 Password、JWT、权限 | 登录、当前用户、受保护请求 |
| 7 | 中间件、CORS | 正式整理 CORS、请求 ID、耗时日志 | 抽出简单 `apiRequest`，仍不用 Axios |
| 8 | SQL 数据库、更大的应用 | SQLModel、事务、APIRouter、持久化 | 刷新页面验证数据不丢失 |
| 9 | Vue 3 Quick Start | API 契约保持稳定 | 把已跑通的 DOM/fetch 迁移到 Vue |
| 10 | JSONL、SSE、后台任务、静态文件 | 导出、事件流、轻量任务 | EventSource 接收真实更新 |
| 11 | 测试、调试及 Advanced 测试章节 | pytest、依赖覆盖、事务/幂等回归 | 真实 API smoke check |
| 12 | Advanced 响应、Cookie/Header、scopes | 文件/CSV 响应、偏好 Cookie、Retry-After、scopes | Blob 下载、Cookie、Header 读取 |
| 13 | Settings、lifespan、代理、中间件 | 配置集中、live/ready、启动资源 | 检查运行状态、统一 API 地址 |
| 14 | WebSockets 及测试 | 讨论房间、多市场订阅 | 原生/Vue WebSocket 收发与清理 |
| 15 | Webhooks、Callbacks、SDK、严格 Content-Type | Webhook 订阅、Oracle 入口、最小 SDK 实验 | 管理页面真实读取订阅/审核结果 |
| 16 | Deployment 与 Vue 生产构建 | 迁移、进程、容器、冒烟检查 | 构建 dist、生产环境真实验收 |

阶段 0—11 是必须完成的主线。阶段 12—16 是进阶主线，但同样坚持“有实际用途才加入，不为覆盖术语而炫技”。

---

# 阶段 0：应用启动、健康检查与第一次真实 fetch


## 进入条件

读完 FastAPI 官方“第一步”。你应知道：

- `FastAPI()` 创建应用对象；
- `@app.get()` 注册 GET 路由；
- 路由函数返回的字典会被转换成 JSON；
- `/docs` 可以调用接口。

## 本阶段目标

- 两个后端都能启动；
- 两个前端都能通过真实 `fetch` 访问各自后端；
- 能区分“网络失败”和“后端返回错误”；
- 不使用静态业务数组。

## 两个项目共用的基础能力

### 本阶段施工清单

- **后端路由**：`GET /health`、`GET /api/v1/info`
- **后端函数**：`build_project_info`

## 后端运行配置：最小 CORS 桥接

你需要在两个 FastAPI 应用中添加相同的 CORS 中间件配置，只允许本地前端地址。

你现在只需要理解：

- 浏览器页面来自 5500 端口；
- API 来自 8000 端口；
- 后端必须明确允许 5500 端口；
- 这不是用户登录，也不是安全认证，只是浏览器的跨源访问许可。

### 接口卡：`GET /health`

#### 建议路由函数名

`health_check`

#### 这个功能解决什么问题

前端启动后，需要确认后端是否真的在线。健康检查接口返回一个很小的 JSON，告诉前端当前应用可访问。

它不检查数据库，不读取文章，也不做复杂操作。

#### 输入

没有路径参数、查询参数或请求体。

#### 后端处理步骤

1. FastAPI 收到 `GET /health`。
2. 路由器找到 `health_check`。
3. 函数构造一个固定字典。
4. FastAPI 把字典转为 JSON。
5. 返回 200。

#### 博客成功返回示例

```json
{
  "project": "blog-system",
  "status": "ok"
}
```

#### 预测市场成功返回示例

```json
{
  "project": "prediction-market",
  "status": "ok"
}
```

#### 为什么返回 `project`

你一次只运行一个项目，因此两个项目都可以使用相同端口；`project` 字段用于确认当前启动的是哪一个后端。博客页面拿到 `prediction-market` 时，应显示“连接到了错误的后端”。

#### 为什么返回 `status`

前端可以使用 `data.status === "ok"` 判断后端是否明确报告正常。

#### 可能失败的情况

此接口本身没有业务错误。常见失败来自网络：

- 后端没有启动；
- URL 或端口写错；
- CORS 配置缺失；
- 前端连接到了错误地址。

这些情况下，可能没有 JSON 响应，JavaScript 会进入 `catch`。

## 前端最小 HTML

博客和预测市场都只需要：

```html
<h1>项目名称</h1>
<button id="check-backend">检查后端</button>
<p id="message">尚未检查</p>
<script src="./scripts/main.js"></script>
```

这里不需要 `ul`、`li`、多层 `div` 或 CSS。

### 前端函数卡：`checkBackend`

#### 用户如何触发

点击“检查后端”按钮。

#### 函数需要找到哪些元素

- 按钮元素；
- `message` 段落。

#### 处理步骤

1. 把消息改为“正在连接……”。
2. 调用 `fetch` 请求 `/health`。
3. 等待得到 `Response`。
4. 检查 `response.ok`。
5. 如果为真，读取 JSON。
6. 检查 `project` 是否与当前页面一致。
7. 显示“后端连接正常”。
8. 如果发生网络错误，显示“无法连接后端，请检查服务和端口”。

#### 为什么先显示“正在连接”

网络请求不是瞬间完成。即使本机很快，也要培养“请求期间有状态”的习惯，避免用户以为按钮没有作用。

#### `response.ok` 是什么

当状态码处于 200—299 时，`response.ok` 为真。404 或 500 时通常为假。

#### 为什么还需要 `try/catch`

`response.ok` 处理的是“服务器有响应，但状态码失败”。

`catch` 处理的是“根本没有正常拿到响应”，例如服务器没启动或网络断开。


> **实现边界：** 只公开项目名、版本和当前开放功能，不公开环境变量与密钥。
**建议完成顺序：** 先跑通 `/health`，再写纯函数，最后让前端验证自己是否连错后端。


## 阶段验收

- 页面不是静态写死“后端正常”，而是点击后真实请求。
- 关闭后端，再点击按钮，页面显示连接失败。
- 启动后端，再点击按钮，页面显示正确项目名称。
- 能解释 `response.ok` 与 `catch` 负责的失败类型不同。

---

# 阶段 1：基础 GET 路由、路径参数与真实列表/详情页面


## 进入条件

读完：

- 路径参数；
- 查询参数。

本阶段**暂时不做分页**。你先掌握“加载列表 → 点击一项 → 加载详情”。分页放到阶段 3，并在那里详细解释 `skip` 和 `limit`。

## 本阶段共同约定

- 后端数据临时放在 Python 列表中；
- 前端不保存替代数据；
- 每次刷新都重新请求后端；
- 文章 ID、事件 ID 都使用整数；
- 后端路由可以先使用普通 `def`，因为目前没有要 `await` 的后端库。

---

## 个人博客系统：文章列表与文章详情
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts`、`GET /api/v1/posts/{post_id}`、`GET /api/v1/posts/{post_id}/related`、`GET /api/v1/posts/latest`
- **后端函数**：`find_post_by_id`、`build_post_summary`


### 建议的内存文章形状

每篇文章至少有：

```json
{
  "id": 1,
  "title": "FastAPI 学习第一天",
  "author": "Hazel",
  "content": "这是正文"
}
```

`id` 用于精确查找；`title` 用于按钮文字；`author` 用于摘要；`content` 只在详情接口返回。

### 接口卡：`GET /api/v1/posts`

#### 建议路由函数名

`list_posts`

#### 这个功能可以做什么

让前端获取所有文章的简短信息，以便创建文章按钮。

#### 为什么列表不返回完整正文

列表页面只需要标题和作者。如果每篇文章正文很长，列表接口全部返回会浪费网络和内存。

因此：

- 列表返回摘要；
- 点击文章后，再请求详情。

这叫做“列表接口”和“详情接口”分工。

#### 输入

本阶段没有输入参数。

#### 处理步骤

1. 遍历内存文章列表。
2. 对每篇文章创建一个新的摘要字典。
3. 摘要只保留 `id`、`title`、`author`。
4. 把所有摘要放进 `items` 列表。
5. 计算文章总数 `total`。
6. 返回结果。

#### 为什么要创建新字典

不要直接把原始文章对象全部返回。创建新字典有两个作用：

- 明确控制公开字段；
- 防止不小心把正文或未来的内部字段暴露到列表响应。

#### 成功返回示例

```json
{
  "items": [
    {"id": 1, "title": "FastAPI 学习第一天", "author": "Hazel"},
    {"id": 2, "title": "请求与响应", "author": "Hazel"}
  ],
  "total": 2
}
```

#### 为什么返回 `items`

前端需要遍历这个数组，为每篇文章创建按钮。

#### 为什么返回 `total`

前端可以显示“共 2 篇文章”。以后加入分页时，`total` 还能判断是否有下一页。

#### 本阶段不返回什么

不返回：

- 完整正文；
- 内部备注；
- 密码；
- 后端 Python 对象引用。

#### 失败情况

内存列表为空不是错误，仍然返回 200：

```json
{
  "items": [],
  "total": 0
}
```

前端看到空数组后显示“暂无文章”。

### 接口卡：`GET /api/v1/posts/{post_id}`

#### 建议路由函数名

`get_post_detail`

#### `{post_id}` 是什么

它是路径参数。

请求：

```text
GET /api/v1/posts/2
```

FastAPI 会把 URL 中的 `2` 传给函数参数 `post_id`。

如果你把参数类型写成 `int`，FastAPI 会尝试把字符串 `"2"` 转成整数 `2`。

#### 这个功能可以做什么

前端点击某篇文章按钮后，通过文章 ID 获取完整正文。

#### 输入

- `post_id`：来自路径，整数。

#### 处理步骤

1. 接收 `post_id`。
2. 遍历文章列表。
3. 比较每篇文章的 `id` 是否等于 `post_id`。
4. 找到后立即返回该文章详情。
5. 遍历结束仍未找到，返回“文章不存在”。

#### 为什么找到后可以立即结束

文章 ID 应唯一。找到目标后继续遍历没有意义。

#### 成功返回示例

```json
{
  "id": 2,
  "title": "请求与响应",
  "author": "Hazel",
  "content": "这里是完整正文"
}
```

#### 不存在时怎么处理

阶段 1 尚未正式学习 `HTTPException`。你可以先返回一个简单错误对象，并在阶段 4 改成真正的 404。

学习重点是：不能直接取一个不存在的位置，也不能让 `None` 后续触发异常。

#### FastAPI 自动 422 示例

请求：

```text
GET /api/v1/posts/abc
```

如果 `post_id` 声明为整数，`abc` 无法转换，FastAPI 会自动返回 422。这个错误发生在进入路由函数之前。

### 后端辅助函数卡：`find_post_by_id`

#### 为什么需要它

列表查找逻辑以后会被详情、修改、删除、发布等多个路由重复使用。

阶段 1 就可以先写一个普通 Python 函数：

- 输入：文章列表和 `post_id`；
- 输出：找到的文章，或 `None`。

#### 详细处理逻辑

1. 逐个查看文章。
2. 比较 `post["id"]` 和 `post_id`。
3. 相等时返回该文章。
4. 循环结束仍未返回，则返回 `None`。

#### 为什么不使用数组下标

文章 ID 为 10，不表示它一定在列表下标 10。删除文章后，ID 也可能不连续。

所以不要写“用 `posts[post_id]` 找文章”。

---

## 博客前端最小 HTML

```html
<h1>个人博客</h1>
<button id="reload-posts">刷新文章</button>
<p id="message">正在等待操作</p>
<section id="post-buttons"></section>
<h2 id="post-title">请选择文章</h2>
<p id="post-author"></p>
<pre id="post-content"></pre>
<script src="./scripts/main.js"></script>
```

### 为什么使用 `section`

它只是一个用于放文章按钮的容器，比多层 `div` 更容易读。你不需要学习复杂语义。

### 为什么正文使用 `pre`

`pre` 会保留文本中的换行。现在先用 `textContent` 显示 Markdown 原文，不做 HTML 渲染，也没有 XSS 风险。

### 前端函数卡：`loadPosts`

#### 什么时候调用

- 页面加载完成时调用一次；
- 点击“刷新文章”时再次调用。

#### 处理步骤

1. 把 `message` 改成“正在加载文章……”。
2. 请求 `GET /api/v1/posts`。
3. 检查 `response.ok`。
4. 读取 JSON 得到 `data`。
5. 清空 `post-buttons` 容器的旧内容。
6. 查看 `data.items.length`。
7. 如果为 0，显示“暂无文章”。
8. 如果大于 0，遍历 `data.items`。
9. 每篇文章创建一个 `button`。
10. 按钮文字可设为“标题 — 作者”。
11. 在按钮点击事件中调用 `loadPostDetail(post.id)`。
12. 把消息改成“共加载 N 篇文章”。

#### “清空旧内容”为什么必要

假设第一次加载创建了两个按钮。再次点击刷新，如果不清空，就会再创建两个相同按钮，页面变成四个。

简单做法是把容器的 `textContent` 设置为空字符串，然后重新创建。

#### 为什么按钮点击时传 `post.id`

标题可能重复，作者也可能重复；ID 才是后端查找文章的稳定标识。

### 前端函数卡：`loadPostDetail`

#### 输入

`postId`：来自按钮绑定的文章 ID。

#### 处理步骤

1. 显示“正在加载文章详情……”。
2. 拼出 URL：`/api/v1/posts/` 加上 `postId`。
3. 发送 GET 请求。
4. 检查状态。
5. 读取 JSON。
6. 把 `data.title` 写入标题元素。
7. 把 `data.author` 写入作者元素。
8. 把 `data.content` 写入 `pre` 的 `textContent`。
9. 显示“文章加载成功”。

#### 为什么不使用 `innerHTML`

文章正文来自后端，将来可能包含用户输入。`innerHTML` 会把文本当 HTML 解释，可能执行危险内容。

现阶段只用 `textContent`，原样显示文本。

---

### 接口卡：`GET /api/v1/posts/{post_id}/related`

**建议路由函数名：** `list_related_posts`

**用户从页面上做什么：** 详情页点击“同作者文章”。

**这个功能为什么值得在本阶段加入：** 练习 path 与 query 同时出现，并理解先找基准资源再筛选。

**输入来自哪里：** `post_id` path；`limit` query，默认 3。

**后端必须按下面顺序处理：**

1. 查当前文章。
2. 遍历其他文章并排除自己。
3. 保留 author 相同的文章。
4. 排序，计算 total，取最多 limit 条。
5. 转换摘要。

**成功时返回什么：** 200，items、total。

**可能失败的情况：** 当前文章不存在；limit 类型错误。

**前端怎样调用和更新页面：** 把结果渲染成少量按钮，点击仍复用详情函数。

**本功能重点函数或语法：** 列表过滤、`continue`、切片。

**本阶段仍然没有解决什么：** 这只是简单关联，不是推荐算法。

### 后端函数卡：`build_post_summary`

**函数类型：** 纯转换函数

**由谁调用：** 文章列表、相关文章、最新文章

**接收什么：** 内部文章字典。

**返回什么：** 只含 id、title、author 的新字典。

**内部处理顺序：**

1. 读取公开字段。
2. 构造新字典。
3. 返回。

**为什么要单独写这个函数：** 多个路由不应重复手写摘要，也不能泄露正文。

**重点语法或方法：** 字典字面量。

**边界与限制：** 缺字段代表后端数据 bug。

### 接口说明卡：`GET /api/v1/posts/latest`
- **建议路由函数名**：`get_latest_post`。
- **用户动作**：点击“查看最新文章”。
- **这个后端功能可以做什么**：提供最新文章快捷入口，并练习静态路由必须放在动态路由之前。
- **输入从哪里来**：无输入。
- **为什么路由顺序重要**：如果先声明 `/posts/{post_id}`，框架可能先尝试把字符串 `latest` 当作 post_id。应先声明固定的 `/posts/latest`，再声明动态的 `/posts/{post_id}`。
- **本阶段“最新”的定义**：还没有 `created_at`，暂时把 ID 最大视为最新。规则必须写清楚，不能一会儿用插入顺序、一会儿用 ID。
- **路由函数的核心职责**：只读地找出符合“最新”规则的一篇文章并返回公开详情，不修改列表，也不创建第二份文章。
- **处理顺序**：
  1. 确认文章集合是否为空。
  2. 使用普通循环维护 `latest_post`：第一次遇到文章先记住；之后遇到更大 ID 就替换。这样比一开始引入复杂表达式更容易跟踪。
  3. 也可以在理解后使用 Python 内置 `max(posts, key=...)`。`max` 返回最大的元素，`key` 告诉它“用每篇文章的 id 比较”，不是让你自己写排序算法。
  4. 构造公开详情对象。
- **成功返回**：200，返回 id、title、content、author。
- **失败返回**：没有文章时本阶段返回明确的临时错误对象；阶段 4 学到 `HTTPException` 后正式改为 404。
- **前端拿到结果后做什么**：`api.js` 的 `fetchLatestPost` 请求固定 URL；`main.js` 把返回对象交给与普通详情相同的 `renderPostDetail`，无需另写一套渲染逻辑。
- **本阶段仍然存在的限制**：当前没有 created_at，只能用 ID 或插入顺序代表最新。

## 事件竞猜与预测市场：事件列表与事件详情
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/events`、`GET /api/v1/events/{event_id}`、`GET /api/v1/events/open`、`GET /api/v1/events/{event_id}/quote`
- **后端函数**：`find_event_by_id`、`calculate_quote_preview`


### 建议的事件形状

```json
{
  "id": 1,
  "question": "明天会下雨吗？",
  "status": "open",
  "options": [
    {"id": 1, "text": "会", "pool_points": 0},
    {"id": 2, "text": "不会", "pool_points": 0}
  ]
}
```

这里只使用整数 ID 和整数积分。

### 接口卡：`GET /api/v1/events`

#### 建议路由函数名

`list_events`

#### 功能

让前端获取事件摘要按钮。

#### 处理步骤

1. 遍历事件列表。
2. 为每个事件创建摘要。
3. 摘要只保留 `id`、`question`、`status`。
4. 返回 `items` 和 `total`。

#### 成功返回示例

```json
{
  "items": [
    {"id": 1, "question": "明天会下雨吗？", "status": "open"}
  ],
  "total": 1
}
```

#### 前端用途

`items` 用来创建事件按钮；`total` 用来显示事件数量。

### 接口卡：`GET /api/v1/events/{event_id}`

#### 建议路由函数名

`get_event_detail`

#### 功能

用户点击事件后，获取问题、状态、每个选项及当前奖池积分。

#### 输入

`event_id`：路径参数，整数。

#### 处理步骤

1. 接收 `event_id`。
2. 调用 `find_event_by_id`。
3. 找不到时返回明确错误。
4. 找到时返回完整公开详情。

#### 成功返回示例

```json
{
  "id": 1,
  "question": "明天会下雨吗？",
  "status": "open",
  "options": [
    {"id": 1, "text": "会", "pool_points": 20},
    {"id": 2, "text": "不会", "pool_points": 10}
  ]
}
```

#### 为什么 `option.id` 和 `option.text` 分开

前端显示中文“会”，提交时使用 ID 1。

以后即使把显示文字改成“是，会下雨”，原来下注仍然指向 ID 1，不会因为文字变化失效。

### 后端辅助函数卡：`find_event_by_id`

#### 为什么单独写这个函数

事件详情、下注、关闭事件、结算事件以后都需要“根据 ID 查事件”。如果每个路由都重新写一遍循环，容易出现某个路由按 `id` 查，另一个路由却误用数组下标。

#### 输入

- `event_id`：前端请求 URL 中携带的整数事件 ID；
- 当前内存事件列表。

#### 完整处理步骤

1. 从事件列表的第一项开始检查。
2. 读取当前事件字典中的 `id`。
3. 把它与传入的 `event_id` 比较。
4. 相等时立即返回当前事件字典。
5. 不相等时继续检查下一项。
6. 循环全部结束仍未找到，返回 `None`。

#### 具体例子

事件列表中的 ID 是 `[1, 4, 8]`，前端请求 `/events/4`：

- 先比较 1 和 4，不相等；
- 再比较 4 和 4，相等；
- 返回 ID 为 4 的事件；
- 不再检查 ID 8。

#### 为什么不能写 `events[event_id]`

Python 列表的下标从 0 开始，而且删除事件后 ID 往往不连续。ID 为 8 的事件完全可能位于列表下标 2。业务 ID 和数组位置不是一回事。

---

## 预测市场前端最小 HTML

```html
<h1>事件竞猜</h1>
<button id="reload-events">刷新事件</button>
<p id="message">正在等待操作</p>
<section id="event-buttons"></section>
<h2 id="event-question">请选择事件</h2>
<p id="event-status"></p>
<section id="event-options"></section>
<script src="./scripts/main.js"></script>
```

### 前端函数卡：`loadEvents`

#### 什么时候调用

- 页面第一次打开时；
- 用户点击“刷新事件”按钮时；
- 创建新事件成功后；
- 后续下注成功，需要重新确认事件统计时。

#### 完整处理步骤

1. 把消息区域改为“正在加载事件……”。
2. 调用 `fetch` 请求 `GET /api/v1/events`。
3. `await` 等待后端返回 `Response`。
4. 检查 `response.ok`。如果为假，读取错误 JSON，并显示 `detail`。
5. 成功时调用 `response.json()` 得到普通 JavaScript 对象 `data`。
6. 把事件按钮容器的 `textContent` 设为空字符串，删除上一次渲染的按钮。
7. 检查 `data.items.length`。为 0 时显示“暂无事件”，并结束函数。
8. 使用 `forEach` 遍历 `data.items`。当前遍历项可命名为 `event`。
9. 为当前事件创建一个 `button`。
10. 把 `event.question` 写入按钮的 `textContent`。
11. 给按钮注册点击事件。点击时调用 `loadEventDetail(event.id)`。
12. 把按钮追加到事件容器。
13. 遍历结束后显示“共加载 `data.total` 个事件”。

#### 前端究竟用了后端的哪些字段

- `data.items`：实际要生成按钮的事件摘要；
- `event.id`：点击按钮后拼详情 URL；
- `event.question`：按钮上给用户看的文字；
- `data.total`：显示总数量，不用前端自己猜。

#### 后端关闭时会发生什么

`fetch` 无法得到正常响应，进入 `catch`。页面应清空可能过期的按钮，显示“无法连接事件后端”，不能继续展示静态假数据。

### 前端函数卡：`loadEventDetail`

#### 处理步骤

1. 请求 `/api/v1/events/{id}`。
2. 将问题写入标题。
3. 将状态写入状态段落。
4. 清空旧选项显示。
5. 遍历 `data.options`。
6. 每个选项创建一个普通段落，显示“选项文字：当前 N 积分”。

本阶段还没有下注按钮，因为 POST 请求体放在阶段 2 学习。


### 接口卡：`GET /api/v1/events/open`

**建议路由函数名：** `list_open_events`

**用户从页面上做什么：** 点击“只看开放事件”。

**这个功能为什么值得在本阶段加入：** 让状态查询有真实用途，并练习静态路由必须放在动态路由前。

**输入来自哪里：** 可选 limit query。

**后端必须按下面顺序处理：**

1. 遍历事件。
2. 只保留 status=open。
3. 计算 total。
4. 限制 items 数量。
5. 转换摘要。

**成功时返回什么：** 200，items、total。

**可能失败的情况：** 无开放事件返回空列表。

**前端怎样调用和更新页面：** 复用事件列表渲染函数。

**本功能重点函数或语法：** 字符串比较、静态路由顺序。

**本阶段仍然没有解决什么：** 截止时间在阶段 2用 datetime 后再同时判断。

### 后端函数卡：`calculate_quote_preview`

**函数类型：** 纯计算函数

**由谁调用：** 事件试算路由

**接收什么：** current_pool、amount_points。

**返回什么：** simulated_pool。

**内部处理顺序：**

1. 检查投入为正整数。
2. 相加并返回。

**为什么要单独写这个函数：** 确认试算不修改事件。

**重点语法或方法：** 整数加法。

**边界与限制：** 不计算赔率或收益。

### 接口说明卡：`GET /api/v1/events/{event_id}/quote`
- **建议路由函数名**：`get_event_quote`。
- **用户动作**：选择选项、输入积分，然后点击“试算”；还没有点击真正下注。
- **这个后端功能可以做什么**：只计算“投入后该选项池会变成多少”。它不是收益保证，也不会保存下注。
- **输入从哪里来**：`event_id` 来自路径；`option_id` 与 `amount_points` 来自查询参数。
- **实际 URL 示例**：`GET /api/v1/events/3/quote?option_id=1&amount_points=20`。
- **路由函数的核心职责**：读取并计算一个说明性结果，绝不能修改事件、余额或池子。
- **处理顺序**：
  1. 查事件。
  2. 查选项。
  3. 检查 amount_points 大于 0。
  4. 读取 `current_option_pool`。例：当前为 40。
  5. 计算局部变量 `simulated_option_pool = 40 + 20 = 60`。
  6. 构造响应。绝不执行 `option["pool_points"] += amount_points`。
- **成功返回示例**：

  ```json
  {
    "event_id": 3,
    "option_id": 1,
    "amount_points": 20,
    "current_option_pool": 40,
    "simulated_option_pool": 60
  }
  ```

- **失败返回**：事件或选项不存在；积分不合法；类型错误 422。
- **怎样证明它只读**：请求前 GET 事件详情记下池子 40；连续调用 quote 两次；再 GET 详情仍应是 40。若变成 80，说明你错误地在 GET 中修改了数据。
- **前端拿到结果后做什么**：显示“当前池 40；若投入 20，模拟池 60”。不要把模拟值直接写进正式事件详情状态，因为用户还没下注。
- **本阶段仍然存在的限制**：试算公式只是教学展示，真实结算规则在数据库阶段明确。

## 阶段 1 验收

- 两个前端页面都不包含硬编码业务数组。
- 刷新按钮会真实请求后端。
- 新增一条后端内存数据并刷新页面后，页面会显示新数据。
- 点击列表项会根据 ID 请求真实详情。
- 详情不存在时，页面显示错误，而不是继续显示上一条详情。
- 能解释为什么列表不返回完整正文。

---

# 阶段 2：请求体、创建功能与第一次真实 POST


## 进入条件

读完：

- 请求体；
- 请求体字段；
- 多个请求体参数；
- 嵌套模型；
- 示例数据；
- 额外数据类型。

## 本阶段重点

- 浏览器把表单值整理成 JavaScript 对象；
- `JSON.stringify()` 把对象转成 JSON；
- 请求头声明 `Content-Type: application/json`；
- 后端 Pydantic 模型验证请求体；
- 成功后前端重新加载真实列表。

## `JSON.stringify()` 为什么需要

JavaScript 对象只存在于浏览器内存中。HTTP 请求体需要文本或字节。

例如浏览器对象：

```text
{ title: "新文章", author: "Hazel", content: "正文" }
```

`JSON.stringify()` 会把它变成 JSON 文本，后端才能解析。

---

## 个人博客系统：创建文章
### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/posts`、`POST /api/v1/posts/preview`
- **后端函数**：`generate_next_post_id`、`normalize_tags`


### 请求模型：`PostCreate`

只包含用户允许提交的字段：

- `title`：字符串；
- `author`：字符串；
- `content`：字符串。

不允许客户端提交：

- `id`；
- 创建时间；
- 浏览量；
- 是否管理员推荐。

这些字段应由服务器决定。

### 接口卡：`POST /api/v1/posts`

#### 建议路由函数名

`create_post`

#### 用户动作

用户在表单输入标题、作者和正文，点击“创建文章”。

#### 输入来源

JSON 请求体。

#### 后端处理顺序

1. FastAPI 读取 JSON。
2. Pydantic 检查必填字段是否存在、类型是否正确。
3. 路由函数接收到已经解析好的 `PostCreate` 对象。
4. 对标题、作者和正文做 `.strip()`，去掉首尾空白。
5. 检查清理后是否为空。
6. 生成下一个文章 ID。
7. 构造完整文章字典。
8. 追加到内存文章列表。
9. 返回新文章。

#### 为什么必须先校验再修改列表

如果先追加文章，后发现标题为空，就会留下半成品数据。

所有可能失败的检查应在“修改数据”之前完成。

#### 成功返回示例

```json
{
  "id": 3,
  "title": "新文章",
  "author": "Hazel",
  "content": "正文"
}
```

阶段 3 再正式把创建状态码设为 201。阶段 2 可以先关注请求体和创建逻辑。

#### 常见错误

- 缺少 `title`：FastAPI 自动 422；
- `title` 不是字符串：FastAPI 自动 422；
- 标题只有空格：路由业务检查失败；
- 正文为空：业务检查失败。

### 后端辅助函数卡：`generate_next_post_id`

#### 输入

文章列表。

#### 输出

一个没有被使用的新整数 ID。

#### 详细逻辑

1. 如果文章列表为空，返回 1。
2. 如果不为空，取出所有文章 ID。
3. 找出最大 ID。
4. 返回最大 ID 加 1。

#### 示例

现有 ID：1、2、5。

最大值是 5，下一个 ID 为 6。

#### 为什么不能用 `len(posts) + 1`

如果原来有 ID 1、2、3，删除 2 后列表长度为 2，`len + 1` 会得到 3，与已有 ID 3 冲突。

## 博客前端新增 HTML

```html
<form id="post-form">
  <input id="post-title" placeholder="标题" required>
  <input id="post-author" placeholder="作者" required>
  <textarea id="post-content" placeholder="正文" required></textarea>
  <button type="submit">创建文章</button>
</form>
```

没有必要做复杂布局。

### 前端函数卡：`handlePostSubmit`

#### 为什么监听 `submit` 而不是只监听按钮 `click`

表单按 Enter 也会提交。监听 `submit` 更符合表单行为。

#### 处理步骤

1. 接收事件对象 `event`。
2. 调用 `event.preventDefault()`，阻止浏览器刷新页面。
3. 读取三个输入框的 `.value`。
4. 对值执行 `.trim()`。
5. 如果有空值，在页面显示提示，不发送请求。
6. 创建请求对象。
7. 调用 `fetch`，方法设为 `POST`。
8. 设置 `Content-Type: application/json`。
9. 请求体使用 `JSON.stringify(payload)`。
10. 等待响应。
11. 读取成功或错误 JSON。
12. 成功时清空表单。
13. 调用 `loadPosts()` 重新从后端获取列表。
14. 调用 `loadPostDetail(newPost.id)` 显示刚创建的文章。

#### 为什么成功后要重新 `loadPosts`

前端不应该自己假装后端已经保存成功。后端成功返回后，再从后端加载列表，页面与后端保持一致。

---

### 接口说明卡：`POST /api/v1/posts/preview`
- **建议路由函数名**：`preview_post`。
- **这个后端功能可以做什么**：提供安全的文本预览统计，练习多个请求体字段，但不把 Markdown 转成 HTML。
- **输入从哪里来**：JSON 请求体包含 title、content、tags；不保存。
- **路由函数的核心职责**：对文本做与创建相同的基础清理，计算字符数、非空行数和估算阅读分钟。
- **处理顺序**：
  1. 验证输入。
  2. 去掉首尾空白。
  3. 按换行统计非空行。
  4. 计算字符数。
  5. 用简单固定规则估算阅读分钟，例如每若干字符一分，并保证最少 1 分钟。
  6. 返回统计，不写入文章集合。
- **成功返回**：200，返回 normalized_title、character_count、non_empty_line_count、estimated_reading_minutes、normalized_tags。
- **失败返回**：输入验证失败自动 422；全空正文先使用本阶段临时业务失败结构，阶段 4 再改正式 400。
- **前端拿到结果后做什么**：编辑器可在用户点击“预览统计”时显示字数和预计阅读时间。
- **本阶段仍然存在的限制**：不是 Markdown HTML 预览，不涉及 XSS。

### 后端函数说明卡：`normalize_tags`
- **函数类型**：纯业务函数
- **由谁调用**：create_post、preview_post、后续 update_post
- **接收什么**：字符串列表。
- **返回什么**：清理并去重后的字符串列表。
- **内部顺序**：
  1. 逐个 strip。
  2. 丢弃空标签。
  3. 按项目规定统一英文大小写；中文原样保留。
  4. 保持第一次出现的顺序去重。
  5. 检查最终数量不超过上限。
- **注意事项**：不接触 FastAPI Request；这样可以直接写单元测试。

## 事件竞猜与预测市场：创建事件与下注
### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/events`、`POST /api/v1/events/{event_id}/bets`
- **后端函数**：`find_option_by_id`、`validate_event_options`


### 请求模型：`EventCreate`

建议只包含：

- `question`：问题；
- `option_texts`：字符串列表，例如 `["会", "不会"]`。

本阶段不急着加入截止时间和复杂状态机。

### 接口卡：`POST /api/v1/events`

#### 建议路由函数名

`create_event`

#### 处理步骤

1. 接收请求体。
2. 清理问题首尾空白。
3. 检查问题非空。
4. 检查选项数量至少为 2。
5. 清理每个选项文字。
6. 检查选项没有空字符串。
7. 检查清理后的选项文字不重复。
8. 生成事件 ID。
9. 为每个选项生成选项 ID。
10. 每个选项的 `pool_points` 初始化为 0。
11. 事件状态初始化为 `open`。
12. 添加到内存列表。
13. 返回新事件。

#### 为什么客户端不提交 `pool_points`

奖池是下注结果，必须由服务器计算。客户端不能说“创建事件时奖池已经有 999999 积分”。

#### 成功返回示例

```json
{
  "id": 2,
  "question": "周末会下雨吗？",
  "status": "open",
  "options": [
    {"id": 1, "text": "会", "pool_points": 0},
    {"id": 2, "text": "不会", "pool_points": 0}
  ]
}
```

## 请求模型：`BetCreate`

- `user_id`：整数；
- `option_id`：整数；
- `amount_points`：正整数。

现在暂时从请求体接收 `user_id`。认证阶段会改为从 JWT 当前用户得到。

### 接口卡：`POST /api/v1/events/{event_id}/bets`

#### 建议路由函数名

`place_bet`

#### 这个功能做什么

用户选择某个事件选项，提交一定数量的虚拟积分。服务器把积分加到该选项奖池，并返回本次结果。

#### 输入

- `event_id`：路径参数；
- `user_id`、`option_id`、`amount_points`：JSON 请求体。

#### 必须严格遵守的处理顺序

1. 根据 `event_id` 查找事件。
2. 事件不存在，停止。
3. 检查事件状态是否为 `open`。
4. 状态不是 `open`，停止。
5. 在该事件的选项中查找 `option_id`。
6. 选项不存在，停止。
7. 检查 `amount_points` 是否大于 0。
8. 所有检查通过后，才修改 `pool_points`。
9. 创建本次下注回执。
10. 返回回执和更新后的选项奖池。

#### 为什么“修改奖池”必须放在所有检查之后

假设先加了积分，后来才发现事件已关闭，就需要回滚修改。初学阶段最简单可靠的方式是：先检查完，再修改一次。

#### 成功返回示例

```json
{
  "bet": {
    "id": 1,
    "user_id": 7,
    "event_id": 1,
    "option_id": 2,
    "amount_points": 20
  },
  "updated_option": {
    "id": 2,
    "text": "不会",
    "pool_points": 30
  }
}
```

#### 为什么返回 `bet`

前端可以明确显示“你刚刚提交了 20 积分到选项 2”，以后还可以保存下注 ID。

#### 为什么返回 `updated_option`

前端可以立即更新该选项的奖池显示，不必猜测后端结果。

不过为了避免其他用户同时下注导致页面过时，成功后仍建议调用 `loadEventDetail(eventId)`，从后端重新获取完整状态。

### 后端辅助函数卡：`find_option_by_id`

#### 输入

- 事件对象；
- `option_id`。

#### 处理逻辑

1. 遍历事件的 `options`。
2. 比较每个选项的 ID。
3. 找到立即返回。
4. 找不到返回 `None`。

#### 为什么必须在“当前事件的选项”里找

不同事件都可能有选项 ID 1。只拿 `option_id` 去全局查找，可能找到别的事件的选项。

---

## 预测市场前端新增 HTML

创建事件表单：

```html
<form id="event-form">
  <input id="event-question-input" placeholder="事件问题" required>
  <input id="option-one-input" placeholder="选项一" required>
  <input id="option-two-input" placeholder="选项二" required>
  <button type="submit">创建事件</button>
</form>
```

下注区域：

```html
<input id="user-id-input" type="number" placeholder="用户 ID">
<input id="bet-amount-input" type="number" placeholder="积分">
<section id="bet-buttons"></section>
<p id="bet-result"></p>
```

### 前端函数卡：`handleEventSubmit`

1. 阻止表单刷新；
2. 读取问题和两个选项；
3. 清理空白；
4. 构造 `{question, option_texts: [one, two]}`；
5. POST JSON；
6. 成功后清空表单；
7. 调用 `loadEvents()`；
8. 显示新事件详情。

### 前端函数卡：`renderBetButtons`

#### 输入

事件详情中的 `options` 和当前 `eventId`。

#### 处理步骤

1. 清空旧下注按钮。
2. 遍历选项。
3. 为每个选项创建一个按钮。
4. 按钮文字显示“押 选项文字”。
5. 点击按钮时调用 `handleBet(eventId, option.id)`。

#### 为什么不从按钮文字推断选项

按钮文字是展示内容，可能修改；`option.id` 才是提交给后端的稳定值。

### 前端函数卡：`handleBet`

1. 读取用户 ID 和积分输入；
2. 使用 `Number()` 转成数字；
3. 检查是否为整数且大于 0；
4. 构造请求体；
5. POST 到当前事件下注路由；
6. 检查响应；
7. 成功时显示回执；
8. 再次调用 `loadEventDetail(eventId)` 获取最新奖池。

#### 为什么前端检查后，后端还要检查

任何用户都可以绕过页面，直接调用 API。前端检查只改善用户体验，后端检查才是业务规则。


### 后端函数说明卡：`validate_event_options`
- **函数类型**：纯业务函数
- **由谁调用**：create_event、后续 update_event
- **接收什么**：选项列表。
- **返回什么**：验证通过时返回清理后的选项列表；失败时抛业务错误。
- **内部顺序**：
  1. 确认至少两个选项。
  2. 确认 option_id 唯一。
  3. 清理 label。
  4. 确认 label 非空且不重复。
- **注意事项**：不使用数组下标作为选项身份；显示顺序改变不会改变 option_id。

## 阶段 2 验收

- 创建文章后，列表和详情来自真实后端。
- 创建事件后，事件按钮来自真实后端。
- 下注成功后，奖池从后端重新加载。
- 不能通过修改前端请求体直接指定文章 ID 或奖池总额。
- 所有数据修改都发生在检查通过之后。

---
# 阶段 3：查询校验、关键字搜索、分页与稳定响应模型


## 进入条件

读完：

- 查询参数和字符串校验；
- 路径参数和数值校验；
- 查询参数模型；
- 响应模型；
- 更多模型；
- 响应状态码。

这一阶段才正式加入你上一版中困惑的 `keyword`、`skip` 和 `limit`。

---

# 3.1 先彻底解释 `keyword`

## `keyword` 是什么

它是用户输入的搜索文字。

例如文章标题有：

- `FastAPI 第一天`
- `Python 类型提示`
- `FastAPI 请求体`

用户输入：

```text
FastAPI
```

前端请求：

```text
GET /api/v1/posts?keyword=FastAPI
```

后端只保留标题中包含 `FastAPI` 的文章。

## 需要写 KMP 吗

**不需要。**

这个项目的目标是练习 Web API，而不是实现字符串匹配算法。Python 已经提供了字符串包含判断：

```text
keyword in title
```

为了忽略大小写，可以把两边都转成小写：

```text
keyword.lower() in title.lower()
```

这已经足够处理学习项目中的几十或几百篇文章。

KMP 适合研究模式匹配算法，或者在特定大规模文本处理中控制算法复杂度。这里手写 KMP 会让搜索功能变得更难读、更难调试，也没有实际收益。

## 为什么先 `.strip()`

用户可能输入三个空格。三个空格 technically 是字符串，但通常应该视为“没有搜索词”。

处理顺序：

1. 如果 `keyword` 是 `None`，表示没有传；
2. 如果传了，执行 `.strip()`；
3. 清理后为空字符串，按“没有搜索条件”处理；
4. 不为空，再进行包含判断。

## 具体示例

原始标题：

```text
FastAPI 第一天
```

搜索词：

```text
fastapi
```

两边转小写后：

```text
"fastapi" in "fastapi 第一天"
```

结果为真，因此保留这篇文章。

---

# 3.2 再彻底解释 `skip` 和 `limit`

## `limit` 是什么

`limit` 表示“这次最多返回多少条”。

例如：

```text
limit = 3
```

表示后端一次最多返回 3 篇文章。

## `skip` 是什么

`skip` 表示“从符合条件的数据开头跳过多少条”。

例如文章按 ID 从大到小排序后为：

```text
[7, 6, 5, 4, 3, 2, 1]
```

### 第一页

```text
skip = 0
limit = 3
```

含义：

- 前面跳过 0 条；
- 最多取 3 条。

结果：

```text
[7, 6, 5]
```

### 第二页

```text
skip = 3
limit = 3
```

含义：

- 跳过前 3 条，也就是 7、6、5；
- 接着最多取 3 条。

结果：

```text
[4, 3, 2]
```

### 第三页

```text
skip = 6
limit = 3
```

跳过前 6 条，只剩：

```text
[1]
```

返回 1 条是正常的。`limit=3` 表示最多 3 条，不是必须凑够 3 条。

## Python 切片在这里怎么用

概念表达式：

```text
items[skip : skip + limit]
```

第一页面：

```text
items[0 : 3]
```

取得下标 0、1、2。

第二页面：

```text
items[3 : 6]
```

取得下标 3、4、5。

Python 切片右边界不包含，因此结束位置使用 `skip + limit`。

## 为什么必须先筛选和排序，再分页

正确顺序：

1. 取得全部文章；
2. 用关键字筛选；
3. 排序；
4. 计算筛选后的 `total`；
5. 再用 `skip` 和 `limit` 截取。

错误顺序示例：先取前三篇，再搜索。

如果匹配文章在第四篇以后，错误顺序会完全找不到它。

## 为什么 `total` 要在分页之前计算

假设一共有 7 篇符合条件，当前页面只返回 3 篇。

- `items.length` 是 3；
- `total` 是 7。

前端需要知道总共有 7 篇，才能判断还有下一页。

如果把 `total` 写成当前页长度 3，前端会误以为没有更多数据。

---

## 个人博客系统：搜索与分页升级
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts`、`GET /api/v1/posts/{post_id}（响应契约升级）`、`POST /api/v1/posts（状态码和输出升级）`
- **后端函数**：本阶段没有新增独立后端函数。


## 查询参数模型：`PostQuery`

建议字段：

- `keyword`：可选字符串；
- `skip`：整数，默认 0，最小 0；
- `limit`：整数，默认 5，最小 1，最大 20。

### 为什么限制 `limit` 最大值

如果用户请求 `limit=1000000`，后端可能一次返回大量数据。

学习项目设 20 足够。限制不是为了刁难用户，而是保护接口。

### 接口卡：`GET /api/v1/posts`（搜索分页版）

#### 建议路由函数名

仍然是 `list_posts`。同一个功能升级，不需要创建 `/posts/search-v2`。

#### 输入示例

```text
GET /api/v1/posts?keyword=fastapi&skip=0&limit=5
```

#### 详细处理顺序

1. FastAPI 解析 `keyword`、`skip`、`limit`。
2. 声明式约束先检查 `skip >= 0`。
3. 声明式约束检查 `1 <= limit <= 20`。
4. 复制或读取文章集合。
5. 如果 `keyword` 存在，执行清理和小写转换。
6. 使用普通字符串 `in` 判断标题是否包含关键字。
7. 对筛选结果按 ID 从大到小排序。
8. 在切片前计算 `total`。
9. 使用 `[skip : skip + limit]` 得到当前页。
10. 把当前页文章转换为摘要。
11. 返回 `items`、`total`、`skip`、`limit`。

#### 成功返回示例

```json
{
  "items": [
    {"id": 7, "title": "FastAPI 响应模型", "author": "Hazel"},
    {"id": 5, "title": "FastAPI 请求体", "author": "Hazel"}
  ],
  "total": 2,
  "skip": 0,
  "limit": 5
}
```

#### 每个返回字段和前端的关系

#### `items`

前端遍历它，创建文章按钮。

#### `total`

前端显示“搜索到 2 篇”，也用于判断下一页是否存在。

#### `skip`

后端把实际使用的跳过数量回传。前端可以把它当作当前分页位置。

#### `limit`

后端回传每页上限。前端可以显示“每页最多 5 篇”。

#### 前端如何判断有没有下一页

判断：

```text
skip + items.length < total
```

例子：

```text
skip = 0
items.length = 5
total = 12
```

0 + 5 < 12，说明后面还有数据。

最后一页：

```text
skip = 10
items.length = 2
total = 12
```

10 + 2 < 12 为假，因此没有下一页。

#### 为什么不用“当前页码”作为后端唯一参数

页码也可以，但 `skip`/`limit` 更直接地表达数据库查询。你可以在前端维护页码，再换算：

```text
skip = (page - 1) * limit
```

本手册前期直接维护 `skip`，少一个换算概念。

## 响应模型：`PostListResponse`

建议包含：

- `items: list[PostSummary]`；
- `total: int`；
- `skip: int`；
- `limit: int`。

### 响应模型有什么实际作用

- `/docs` 明确展示响应字段；
- FastAPI 检查你的返回形状；
- 未声明的内部字段不会意外输出；
- 前端能稳定依赖字段名称。

## 前端新增最小 HTML

```html
<input id="keyword-input" placeholder="搜索标题">
<button id="search-posts">搜索</button>
<button id="previous-posts">上一页</button>
<button id="next-posts">下一页</button>
<p id="page-info"></p>
```

## 前端状态变量

在 `main.js` 顶部维护：

- `currentPostSkip = 0`；
- `postLimit = 5`；
- `currentKeyword = ""`；
- `lastPostTotal = 0`。

### 这些变量分别表示什么

- `currentPostSkip`：当前跳过多少篇；
- `postLimit`：每次最多请求多少篇；
- `currentKeyword`：当前搜索词；
- `lastPostTotal`：后端上次告诉你的总匹配数量。

### 前端函数卡：`loadPosts`（分页版）

#### URL 如何构造

基础路径：

```text
/api/v1/posts
```

查询字符串：

```text
?keyword=fastapi&skip=0&limit=5
```

对于初学阶段，可以使用 `URLSearchParams`。它是浏览器提供的工具，用来正确拼接和转义查询参数。

#### 为什么不用手工字符串拼接所有参数

用户输入可能包含空格、中文、`&` 等特殊字符。`URLSearchParams` 会进行 URL 编码，减少拼接错误。

#### 处理步骤

1. 根据当前状态创建查询参数。
2. 发 GET 请求。
3. 检查响应。
4. 读取 JSON。
5. 保存 `data.total` 到 `lastPostTotal`。
6. 根据 `data.items` 渲染按钮。
7. 页面显示：
   - 当前显示第几条到第几条；
   - 总数量；
   - 当前搜索词。
8. 如果 `skip === 0`，禁用“上一页”。
9. 如果 `skip + items.length >= total`，禁用“下一页”。

#### 当前显示范围怎么计算

如果当前有数据：

```text
start = skip + 1
end = skip + items.length
```

例子：`skip=5`，当前返回 3 条。

页面显示：

```text
正在显示第 6—8 条，共 12 条
```

如果 `items` 为空，显示“没有符合条件的文章”。

### 前端函数卡：`goToNextPostPage`

#### 处理步骤

1. 先判断是否有下一页。
2. `currentPostSkip += postLimit`。
3. 调用 `loadPosts()`。

#### 为什么不是加 1

`skip` 表示跳过条数，不是页码。

每页 5 条，下一页需要从跳过 5 条变成跳过 10 条，所以加 `limit`。

### 前端函数卡：`goToPreviousPostPage`

1. `currentPostSkip -= postLimit`；
2. 使用 `Math.max(0, ...)` 防止负数；
3. 调用 `loadPosts()`。

### 前端函数卡：`searchPosts`

1. 读取关键字；
2. 保存为 `currentKeyword`；
3. 把 `currentPostSkip` 重置为 0；
4. 调用 `loadPosts()`。

#### 为什么搜索时必须回第一页

用户原来可能在无搜索条件的第 4 页。搜索后总共只有 2 条，如果仍然 `skip=15`，会得到空页。

---

### 接口说明卡：`GET /api/v1/posts/{post_id}（响应契约升级）`
- **建议路由函数名**：`get_post_detail`。
- **这个后端功能可以做什么**：返回 PostDetail，确保内部备注、密码相关字段永远不出现在响应。
- **输入从哪里来**：路径 post_id；可选 Cookie `reading_mode`，只影响一个无安全性的显示提示，例如 compact/full。
- **路由函数的核心职责**：查文章并构造公开详情；Cookie 只决定返回一个 display_mode 字段，不改变权限。
- **处理顺序**：
  1. 查找文章。
  2. 构造 PostDetail。
  3. 读取 reading_mode；不合法时使用默认值。
  4. 返回公开对象。
- **成功返回**：200，包含 id、title、content、author、tags、created_at、updated_at、display_mode。
- **失败返回**：当前文章不存在仍等阶段 4 改正式 404；路径类型错误 422。
- **前端拿到结果后做什么**：前端根据 display_mode 决定是否默认折叠附加信息；正文仍用 textContent。
- **本阶段仍然存在的限制**：Cookie 不是身份，用户可任意修改。

### 接口说明卡：`POST /api/v1/posts（状态码和输出升级）`
- **建议路由函数名**：`create_post`。
- **这个后端功能可以做什么**：明确创建操作返回 201，并只返回 PostDetail。
- **输入从哪里来**：PostCreate 请求体。
- **路由函数的核心职责**：创建后交给输出模型过滤，不能把内部字段一起返回。
- **处理顺序**：
  1. 执行阶段 2 的清理与创建。
  2. 构造内部对象。
  3. 保存。
  4. 通过 PostDetail 输出。
- **成功返回**：201，返回公开详情。
- **失败返回**：422 模型错误；业务冲突暂待阶段 4。
- **前端拿到结果后做什么**：前端以 201 视为创建成功，并使用返回 ID。
- **本阶段仍然存在的限制**：尚无认证。

## 事件竞猜与预测市场：状态筛选和分页
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/events`、`POST /api/v1/events/{event_id}/bets（幂等原型）`、`GET /api/v1/events/{event_id}（响应契约升级）`
- **后端函数**：本阶段没有新增独立后端函数。


## 查询参数模型：`EventQuery`

建议字段：

- `status`：可选字符串；
- `keyword`：可选字符串；
- `skip`：默认 0；
- `limit`：默认 5。

### 接口卡：`GET /api/v1/events`（筛选分页版）

#### 详细处理顺序

1. 解析查询参数。
2. 如果传入 `status`，检查它是否属于允许状态列表：`open`、`closed`、`settled`、`cancelled`。
3. 如果有 `keyword`，用普通 `in` 检查问题文字。
4. 如果有 `status`，只保留状态相同的事件。
5. 按事件 ID 从大到小排序。
6. 计算 `total`。
7. 用 `skip/limit` 切片。
8. 返回事件摘要。

#### 为什么状态检查不用复杂类型

本项目先用普通字符串和一个允许值列表。逻辑更直观：

```text
if status not in ALLOWED_STATUSES
```

以后你理解 Enum 后可以替换，但不是当前必须项。

#### 成功响应示例

```json
{
  "items": [
    {"id": 5, "question": "比赛会加时吗？", "status": "open"}
  ],
  "total": 1,
  "skip": 0,
  "limit": 5
}
```

## 预测市场前端筛选

HTML 只需要：

```html
<input id="event-keyword-input" placeholder="搜索事件">
<select id="event-status-input">
  <option value="">全部状态</option>
  <option value="open">开放</option>
  <option value="closed">已关闭</option>
  <option value="settled">已结算</option>
</select>
<button id="search-events">搜索</button>
<button id="previous-events">上一页</button>
<button id="next-events">下一页</button>
```

### 为什么这里可以使用 `select`

状态只有少量固定值。下拉框比让用户自由输入更不容易拼错。

前端分页逻辑与博客完全相同。重复逻辑是正常的练习，暂时不要为了消除几行代码写复杂通用框架。

---

### 前端函数卡：`loadEvents`（筛选分页升级版）

#### 这个函数和阶段 1 的 `loadEvents` 有什么关系

函数名字不变，因为用户仍然是在“加载事件列表”。只是现在多了筛选条件和分页状态。不要为了每次升级都创建 `loadEventsV2`、`loadEventsV3`。

#### 它依赖哪些前端变量

- `currentEventKeyword`：当前搜索文字；
- `currentEventStatus`：当前状态筛选；
- `currentEventSkip`：当前跳过数量；
- `eventLimit`：每页最多数量；
- `lastEventTotal`：上一次响应的总数量。

这些只是普通变量，不需要状态管理库。

#### 完整处理顺序

1. 把消息改为“正在加载事件……”。
2. 禁用搜索、上一页、下一页按钮，防止同一时刻重复点击。
3. 创建 `URLSearchParams`。
4. keyword 清理后不为空才加入参数。
5. status 不为空才加入参数。
6. 始终加入 skip 和 limit。
7. 请求 `GET /api/v1/events?...`。
8. 检查 response.ok；失败时读取后端错误 JSON。
9. 读取成功 JSON。
10. 保存 `data.total` 到 `lastEventTotal`。
11. 清空旧事件按钮。
12. 遍历 `data.items` 创建新按钮。
13. 点击按钮调用阶段 1 已有的 `loadEventDetail(event.id)`。
14. 计算当前显示范围。
15. 更新上一页、下一页是否可用。
16. 在 `finally` 中恢复搜索按钮，并按当前数据重新决定翻页按钮状态。

#### 前端怎样使用返回字段

- `items`：创建事件按钮；
- `total`：显示符合条件的事件总数；
- `skip`：确认后端实际使用的起点；
- `limit`：确认本次页面大小。

不要假设后端一定原样接受所有参数。后端将实际值回传，页面应以响应为准。

---

### 前端函数卡：`searchEvents`

#### 用户动作

输入关键词、选择状态，再点击“搜索”。

#### 处理顺序

1. 读取关键词输入框。
2. 执行 `.trim()`。
3. 读取状态下拉框 value。
4. 保存到当前筛选变量。
5. 把 `currentEventSkip` 设为 0。
6. 调用 `loadEvents()`。

#### 为什么状态值不直接使用按钮文字

下拉框显示可以是中文“已关闭”，提交值使用后端约定的 `closed`。展示文字可以变化，机器值应稳定。

---

### 前端函数卡：`goToNextEventPage`

#### 处理顺序

1. 先判断 `currentEventSkip + 当前items长度 < lastEventTotal`。
2. 没有下一页时直接结束，不发送无意义请求。
3. 有下一页时 `currentEventSkip += eventLimit`。
4. 调用 `loadEvents()`。

#### 为什么不把当前列表直接删除前几项

下一页必须由后端按当前搜索和状态条件重新查询。前端本地删除数组不能代表数据库中的下一页。

---

### 前端函数卡：`goToPreviousEventPage`

#### 处理顺序

1. `currentEventSkip -= eventLimit`。
2. 使用 `Math.max(0, currentEventSkip)` 防止负数。
3. 调用 `loadEvents()`。

#### 一个具体例子

当前 skip=10、limit=5，上一页后 skip=5。

当前 skip=3、limit=5 时，理论上不应出现这种非整页位置；即使出现，`Math.max(0, 3-5)` 会回到 0。


# 3.3 创建操作为什么返回 201

200 表示一般成功。

201 更明确地表示“服务器成功创建了一个新资源”。

因此本阶段把：

- 创建文章；
- 创建事件；
- 创建下注；

的成功状态码改为 201。

前端仍然可以使用 `response.ok` 判断，不需要把 200 和 201 写成两个完全不同流程。

---

# 3.4 请求 Header 和 Cookie 只做小练习

本阶段可以读取一个无安全意义的请求头：

```text
X-Client-Name: vanilla-blog-frontend
```

它只是告诉后端请求来自哪个学习页面，不能作为用户身份。

可以读取一个 Cookie 作为页面偏好，例如 `page_size=5`，但不要用 Cookie 保存管理员权限。真正身份验证在阶段 6。


### 接口说明卡：`POST /api/v1/events/{event_id}/bets（幂等原型）`
- **建议路由函数名**：`place_bet`。
- **这个后端功能可以做什么**：通过 `Idempotency-Key` 请求头识别同一次用户操作的重试，避免双击或网络重试重复增加奖池。
- **输入从哪里来**：路径 event_id；BetCreate 请求体；请求 Header `Idempotency-Key` 为非空字符串。
- **路由函数的核心职责**：在内存映射中检查该用户和该键是否已经处理。首次处理才写入；重复且内容一致时返回第一次回执。
- **处理顺序**：
  1. 验证 Header 和 body。
  2. 生成请求摘要：event_id、user_id、option_id、amount_points。
  3. 查找 `(user_id, key)`。
  4. 若存在且摘要一致，直接返回旧回执。
  5. 若存在但摘要不同，返回冲突。
  6. 若不存在，执行下注并保存摘要与回执。
- **成功返回**：首次成功 201；一致重试可以返回 200 或 201，本手册建议重试返回 200并明确 `replayed=true`。
- **失败返回**：缺少/格式错误 422；同键不同内容 409；事件业务错误阶段 4 完善。
- **前端拿到结果后做什么**：前端一次点击生成一个 key；同一次请求重试复用同一 key，新的下注生成新 key。
- **本阶段仍然存在的限制**：内存幂等记录重启会丢失，多进程不共享；阶段 8用数据库唯一约束。

### 接口说明卡：`GET /api/v1/events/{event_id}（响应契约升级）`
- **建议路由函数名**：`get_event_detail`。
- **这个后端功能可以做什么**：只返回公开市场数据，不泄露管理员备注或其他用户下注详情。
- **输入从哪里来**：路径 event_id。
- **路由函数的核心职责**：将内部事件转换为 EventPublicDetail。
- **处理顺序**：
  1. 查事件。
  2. 汇总每个选项池。
  3. 计算 total_pool_points。
  4. 过滤 internal_note、settlement_debug 等内部字段。
- **成功返回**：200，返回公开详情。
- **失败返回**：路径错误 422；不存在的正式 404到阶段 4。
- **前端拿到结果后做什么**：事件页渲染问题、状态、截止时间、选项和池子。
- **本阶段仍然存在的限制**：个人下注记录需要单独接口，不能塞进公共详情。

## 阶段 3 验收

- 能用具体数组解释 `skip=3, limit=3` 得到哪些元素。
- 知道 KMP 不属于当前搜索实现。
- 搜索后分页会回到 `skip=0`。
- 前端能根据 `total` 判断下一页。
- 返回模型不会泄漏文章正文到列表接口。
- 创建成功使用 201。

---

# 阶段 4：HTTPException、PATCH、DELETE 与 Markdown 文件上传


## 进入条件

读完：

- 表单数据；
- 表单模型；
- 请求文件；
- 请求表单与文件；
- 处理错误；
- 路径操作配置；
- JSON 兼容编码器；
- 请求体更新数据。

## 本阶段共同重点

- 用 `HTTPException` 返回真正的 404、409 等错误；
- 前端读取后端 `detail`；
- PATCH 只修改用户实际提交的字段；
- 删除前先确认目标存在；
- 上传使用 `FormData`，不手写 multipart 的 `Content-Type`。

---

## 4.1 统一错误处理基础

### 404

资源不存在。例如文章 ID 999 不存在。

### 409

资源存在，但当前状态与操作冲突。例如已关闭事件不能下注。

### 422

请求数据形状或字段约束不通过。很多情况由 FastAPI 自动生成。

### 前端处理顺序

1. 得到 `Response`；
2. 调用 `response.json()` 读取成功或错误体；
3. 如果 `!response.ok`，显示 `data.detail`；
4. 不继续执行成功分支。

注意：错误响应也可能是 JSON，所以不要只在成功时解析。

---

## 个人博客系统：编辑、删除和上传 Markdown
### 本项目本阶段施工清单

- **后端路由**：`PATCH /api/v1/posts/{post_id}`、`DELETE /api/v1/posts/{post_id}`、`POST /api/v1/posts/import`、`PUT /api/v1/posts/{post_id}`
- **后端函数**：`read_markdown_with_limit`、`validate_markdown_upload`


## 请求模型：`PostUpdate`

字段全部可选：

- `title`；
- `author`；
- `content`。

“可选”不是说字段值随便，而是说 PATCH 请求可以只提交其中一项。

### 接口卡：`PATCH /api/v1/posts/{post_id}`

#### 建议路由函数名

`update_post`

#### 用户动作

用户选择一篇文章，修改标题或正文，点击“保存修改”。

#### 输入

- `post_id`：路径参数；
- 修改字段：JSON 请求体。

#### 详细处理顺序

1. 根据 ID 查找文章。
2. 不存在则抛 404。
3. 把请求模型转换为字典，使用 `exclude_unset=True`。
4. 检查是否至少提交了一个字段。
5. 对每个实际提交字段进行清理和验证。
6. 所有字段检查通过后，才修改文章对象。
7. 返回修改后的详情。

#### `exclude_unset=True` 到底解决什么问题

假设更新模型有三个可选字段：标题、作者、正文。

用户只提交：

```json
{
  "title": "新标题"
}
```

你只想修改标题。

如果不区分“没提交”和“提交了空值”，可能把作者和正文错误地改成 `null`。

`exclude_unset=True` 会只保留请求中实际出现的字段。

#### 成功返回

200，返回完整更新后的文章详情。

#### 错误

- 404：文章不存在；
- 400：没有提交任何更新字段；
- 422：字段类型或长度不正确。

### 接口卡：`DELETE /api/v1/posts/{post_id}`

#### 建议路由函数名

`delete_post`

#### 处理步骤

1. 查找文章。
2. 不存在则 404。
3. 记录要删除的文章 ID 和标题，用于返回。
4. 从内存集合删除。
5. 返回删除确认。

#### 成功返回示例

```json
{
  "deleted": true,
  "id": 3,
  "title": "已删除文章"
}
```

#### 为什么不马上使用 204

204 响应不能带响应体。对于初学者，返回删除确认更容易观察前后端交流。

以后高级响应阶段再练习 204。

### 接口卡：`POST /api/v1/posts/import`

#### 建议路由函数名

`import_markdown_post`

#### 用户动作

用户选择一个 `.md` 文件，并填写作者，点击“导入”。

#### 输入来源

`multipart/form-data`：

- `file`：上传文件；
- `author`：普通表单字段。

#### 为什么不能使用 JSON 上传文件

JSON 适合文本和结构化数据，不适合直接发送浏览器选中的文件对象。

`FormData` 能在一个请求中同时携带文件和普通文本字段。

#### 后端处理顺序

1. 检查文件名是否存在。
2. 检查扩展名是否为 `.md`。
3. 检查作者清理后非空。
4. 分块读取文件。
5. 每读一块就累计字节数。
6. 超过上限立即停止并返回错误。
7. 全部读取后尝试 UTF-8 解码。
8. 解码失败则拒绝。
9. 从文件名或正文第一行得到标题；规则必须固定说明。
10. 生成文章 ID。
11. 构造文章并保存。
12. 返回新文章。

#### 为什么分块读取

如果先把整个巨大文件全部读入内存，再检查大小，限制已经失去意义。

分块读取允许在超过上限时提前停止。

#### 为什么扩展名检查不等于绝对安全

用户可以把任意文件改名为 `.md`。因此还要：

- 限制大小；
- 尝试 UTF-8 解码；
- 不执行文件内容；
- 前端先以纯文本显示。

#### 成功返回

201，返回文章详情。

#### 错误

- 400：文件名或作者无效；
- 413：文件过大；
- 415：不是允许的文件类型；
- 422：表单字段缺失。

### 后端辅助函数卡：`read_markdown_with_limit`

#### 输入

- `UploadFile`；
- 最大字节数，例如 100 KB。

#### 输出

成功时返回解码后的字符串。

#### 处理逻辑

1. 准备空的字节块列表和累计大小 0。
2. 每次读取固定大小，例如 4096 字节。
3. 没有更多数据时结束。
4. 累加当前块大小。
5. 如果累计超过上限，抛错误。
6. 保存当前块。
7. 循环结束后合并字节块。
8. UTF-8 解码。

#### 为什么这是辅助函数而不是全塞路由

路由应该描述 HTTP 流程；文件读取规则可以单独测试和复用。

---

### 博客前端函数卡：`handleUpdateSubmit`

1. 取得当前选中的文章 ID；
2. 读取用户真正修改的字段；
3. 只把需要修改的字段放进对象；
4. PATCH JSON；
5. 错误时显示后端说明；
6. 成功后刷新列表和详情。

#### 前端如何只提交有变化的字段

最简单方式：

- 表单始终允许用户编辑三个字段；
- 与加载详情时保存的原值比较；
- 不同的字段才放入 payload。

如果觉得比较暂时太复杂，也可以提交所有字段，但那更接近 PUT，不是严格 PATCH 练习。

### 博客前端函数卡：`handleDelete`

1. 确认当前有选中文章；
2. 使用浏览器 `confirm()` 做最简单确认；
3. 发 DELETE；
4. 成功后清空详情区域；
5. 调用 `loadPosts()`。

`confirm()` 不美观，但前期不追求视觉效果，够用。

### 博客前端函数卡：`handleImportSubmit`

1. 从文件输入框取得 `files[0]`；
2. 没有文件则提示；
3. 创建 `new FormData()`；
4. `append("file", file)`；
5. `append("author", author)`；
6. POST 请求，body 直接使用 FormData；
7. **不要手动设置 `Content-Type`**；
8. 成功后刷新列表和详情。

#### 为什么不能手动设置 multipart Content-Type

浏览器需要自动加入 boundary 分隔符。你手写简单的 `multipart/form-data` 往往缺少 boundary，后端无法正确解析。

---

### 接口说明卡：`PUT /api/v1/posts/{post_id}`
- **建议路由函数名**：`replace_post`。
- **这个后端功能可以做什么**：练习完整替换语义：客户端必须提交文章全部可编辑字段。
- **输入从哪里来**：路径 post_id；完整 PostReplace 请求体。
- **路由函数的核心职责**：先查资源，再用请求体完整替换 title、content、author、tags；保留服务端 id、created_at。
- **处理顺序**：
  1. 查文章。
  2. 验证完整请求体。
  3. 检查冲突。
  4. 保留不可变字段。
  5. 替换可编辑字段并更新 updated_at。
- **成功返回**：200，返回替换后的详情。
- **失败返回**：404、409、422。
- **前端拿到结果后做什么**：前端通常不必实现；这是 `/docs` 中的语义练习。实际编辑主用 PATCH。
- **本阶段仍然存在的限制**：不要同时让 PUT 和 PATCH 行为完全一样。

### 后端函数说明卡：`validate_markdown_upload`
- **函数类型**：普通业务函数
- **由谁调用**：import_markdown_post
- **接收什么**：UploadFile 和最大字节数。
- **返回什么**：验证通过的 UTF-8 文本与原始文件名。
- **内部顺序**：
  1. 检查文件名/后缀。
  2. 分块读取并累计。
  3. 超过上限停止。
  4. 合并有限字节并解码。
  5. 检查内容不是全空。
- **注意事项**：原始 filename 不可直接拼路径；content_type 不能作为唯一可信依据。

## 事件竞猜与预测市场：编辑、关闭、取消
### 本项目本阶段施工清单

- **后端路由**：`PATCH /api/v1/events/{event_id}`、`POST /api/v1/events/{event_id}/close`、`POST /api/v1/events/{event_id}/cancel`
- **后端函数**：本阶段没有新增独立后端函数。


## 请求模型：`EventUpdate`

可选字段：

- `question`；
- `option_texts`。

本阶段规则：一旦事件已经有下注，不允许修改选项，只允许修改问题文字。

### 接口卡：`PATCH /api/v1/events/{event_id}`

#### 处理步骤

1. 查事件，不存在 404。
2. 检查事件是否处于 `open`。
3. 读取实际提交字段。
4. 如果提交了选项修改，检查当前所有奖池是否为 0。
5. 有任何下注时，拒绝修改选项，返回 409。
6. 验证新问题或选项。
7. 所有检查通过后修改。
8. 返回更新后的事件。

#### 为什么有下注后不能改选项

用户下注的是某个明确选项。管理员事后把“会”改成“不会”，会改变下注含义。

显示文字的小修正可以另定严格规则，但初学阶段直接禁止最清楚。

### 接口卡：`POST /api/v1/events/{event_id}/close`

#### 建议路由函数名

`close_event`

#### 功能

停止接收新下注，但尚未决定获胜选项。

#### 处理步骤

1. 查事件；
2. 不存在 404；
3. 如果已经 `closed`，可返回当前状态或 409，项目应统一；
4. 如果已 `settled` 或 `cancelled`，返回 409；
5. 把状态从 `open` 改成 `closed`；
6. 返回事件详情。

#### 前端交互

管理员点击“关闭事件”；成功后重新加载详情。普通下注按钮根据状态禁用。

### 接口卡：`POST /api/v1/events/{event_id}/cancel`

#### 建议路由函数名

`cancel_event`

#### 功能

取消事件。当前内存阶段如果已有下注，只记录取消状态；退款在数据库阶段实现。

#### 处理步骤

1. 查事件；
2. 已结算则不能取消；
3. 已取消时避免重复修改；
4. 设置状态 `cancelled`；
5. 返回事件和提示。

#### 为什么现在不做退款

当前还没有真实用户余额和账本。假装退款会产生不存在的资金状态。

文档必须明确“已知限制”，而不是用一个数字加减冒充完整退款系统。

### 前端函数卡：`handleCloseEvent`

1. 取得当前事件 ID；
2. POST 到 close 路由；
3. 成功后重新加载详情；
4. 如果状态不再 open，禁用下注按钮；
5. 显示后端返回的状态。

### 前端函数卡：`handleCancelEvent`

流程与关闭相似，但页面显示“事件已取消，当前阶段尚未实现余额退款”。


## 阶段 4 验收

- 不存在资源使用真正 404。
- 关闭事件后，下注返回 409。
- PATCH 不会把未提交字段清空。
- 上传文件超过限制时不会创建文章。
- 前端使用 `FormData`，不手写 multipart Content-Type。
- 删除或修改成功后，页面重新从后端加载。

---

# 阶段 5：依赖注入——先重构重复逻辑，不增加花哨功能


## 进入条件

读完依赖项全部章节：

- 基础依赖；
- 类作为依赖；
- 子依赖；
- 装饰器依赖；
- 全局依赖；
- 使用 `yield` 的依赖。

## 这一阶段为什么不新增很多业务功能

依赖注入的重点不是“再造一个 XP 系统”或“突然写复杂限流”。它首先解决的是：

- 多个路由重复解析分页参数；
- 多个路由重复查文章；
- 多个路由重复查事件；
- 多个写操作重复检查事件状态；
- 以后数据库 Session 需要统一创建和关闭。

所以本阶段以**重构现有功能**为主。前端行为不变，仍然真实调用 API。

---

## 两个项目共用的依赖基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`get_pagination`

### 后端依赖函数卡：`get_pagination`

#### 解决什么重复

博客列表和事件列表都需要：

- `skip >= 0`；
- `1 <= limit <= 20`。

如果每个路由重复写，规则可能不一致。

#### 输入

查询参数 `skip` 和 `limit`。

#### 输出

一个简单对象或字典：

```json
{
  "skip": 0,
  "limit": 5
}
```

#### 路由如何使用

路由不再直接声明两个参数，而是接收依赖返回的 pagination。

然后读取：

```text
pagination.skip
pagination.limit
```

或者字典键。

#### 处理步骤

1. FastAPI 先解析查询参数；
2. 验证范围；
3. 创建分页对象；
4. 把它注入列表路由；
5. 路由使用结果切片。

#### 前端是否需要修改

不需要。URL 和返回格式没有变化。

这正是好的重构：内部结构更清楚，对外接口保持兼容。

---

## `yield` 依赖最小练习：`request_timer`

### 为什么需要练习 `yield`

数据库阶段的 Session 依赖会使用：

1. 请求前创建资源；
2. `yield` 给路由；
3. 请求结束后关闭资源。

现在先用一个不改变 API 的计时依赖理解生命周期。

### 处理步骤

1. `yield` 前记录开始时间；
2. `yield` 让路由继续执行；
3. 路由完成或报错后进入 `finally`；
4. 计算耗时；
5. 打印到控制台。

### 为什么使用 `try/finally`

即使路由抛异常，也要执行清理或记录逻辑。

### 为什么暂时不把耗时写进响应头

设置自定义响应头属于后续高级响应内容。现在只打印控制台，避免知识越级。

---

## 个人博客系统

### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/posts/{post_id}/reading-events`、`GET /api/v1/readers/current/xp`
- **后端函数**：`get_post_or_404`、`get_reader_context`、`ReadingRewardPolicy.__call__`、`calculate_reader_level`

### 后端依赖函数卡：`get_post_or_404`

#### 解决什么重复

这些路由都要查文章：

- 获取详情；
- 更新；
- 删除；
- 导入后的后续操作；
- 以后发布和评论。

#### 输入

`post_id` 路径参数。

#### 输出

找到的文章对象。

#### 处理步骤

1. 接收路径中的 `post_id`；
2. 调用 `find_post_by_id`；
3. 找不到时抛 404；
4. 找到时返回文章；
5. FastAPI 把文章注入真正的路由函数。

#### 路由函数因此可以变成什么样

更新路由不再关心“怎么查找和怎么返回 404”，它直接得到一个确定存在的文章，然后专注更新字段。

#### 为什么它是依赖，不只是普通辅助函数

普通函数也能查找。依赖的额外价值是：

- FastAPI 自动取得路径参数；
- 统一异常；
- 以后可以继续依赖数据库 Session；
- `/docs` 和参数解析仍由框架管理。

---

### 后端函数说明卡：`get_reader_context`
- **函数类型**：依赖函数
- **由谁调用**：阅读积分和读者信息路由
- **接收什么**：请求 Header `X-Reader-Id`，阶段 5临时使用字符串或整数文本。
- **返回什么**：读者上下文对象：reader_id、is_anonymous。
- **内部顺序**：
  1. 读取 Header。
  2. 缺失时返回匿名上下文。
  3. 存在时检查格式和长度。
  4. 不把它当真实认证。
- **注意事项**：任何客户端都能伪造 Header，因此只能做教学积分；阶段 6后使用当前登录用户。

### 后端函数说明卡：`ReadingRewardPolicy.__call__`
- **函数类型**：可调用类实例依赖或普通策略函数
- **由谁调用**：POST 阅读事件路由
- **接收什么**：文章、读者上下文和配置的 reward_points。
- **返回什么**：本次应该增加的积分数量；匿名时可以返回 0。
- **内部顺序**：
  1. 确认读者不是匿名。
  2. 确认文章存在且可公开阅读。
  3. 根据配置返回固定奖励，例如 10分。
- **注意事项**：这里不直接修改 XP，避免依赖执行到一半就产生副作用；真正写入由业务函数完成。

### 接口说明卡：`POST /api/v1/posts/{post_id}/reading-events`
- **建议路由函数名**：`create_reading_event`。
- **这个后端功能可以做什么**：在用户明确点击“完成阅读/领取阅读积分”时记录一次阅读事件。它使用 POST，避免普通 GET 详情产生隐藏副作用。
- **输入从哪里来**：路径 post_id；X-Reader-Id 请求头；无请求体。
- **路由函数的核心职责**：组合文章依赖、读者上下文和奖励策略；成功后写入阅读事件并更新内存 XP。
- **处理顺序**：
  1. 依赖先得到文章或抛 404。
  2. 依赖得到读者上下文。
  3. 匿名用户直接返回不累计说明，或按项目规则 400；建议返回 200且 awarded_points=0。
  4. 检查同一读者是否在过短时间内重复领取；重复时返回冲突或 awarded_points=0。
  5. 创建 reading_event_id。
  6. 最后更新该读者 XP。
  7. 计算等级并返回。
- **成功返回**：201。返回 reading_event_id、post_id、reader_id、awarded_points、total_xp、level。
- **失败返回**：文章不存在 404；读者格式错误 422；重复领取 409或按规则返回 200。本手册建议 409，code=READING_REWARD_ALREADY_CLAIMED。
- **前端拿到结果后做什么**：文章详情页面放一个“完成阅读并领取积分”按钮；成功后更新 XP 区域。
- **本阶段仍然存在的限制**：读者身份可伪造，XP 只存在单进程内存。

### 接口说明卡：`GET /api/v1/readers/current/xp`
- **建议路由函数名**：`get_current_reader_xp`。
- **这个后端功能可以做什么**：查看当前临时读者的总 XP 和等级。
- **输入从哪里来**：X-Reader-Id 请求头。
- **路由函数的核心职责**：读取内存 XP，不产生任何奖励。
- **处理顺序**：
  1. 得到 reader context。
  2. 匿名返回 total_xp=0、level=0。
  3. 实名临时读者查内存记录。
  4. 计算等级。
- **成功返回**：200，返回 reader_id、total_xp、level。
- **失败返回**：Header 格式错误 422。
- **前端拿到结果后做什么**：页面初始化或领取奖励后可刷新徽章。
- **本阶段仍然存在的限制**：阶段 6后应改为认证用户，不继续依赖自定义 Header。

### 后端函数说明卡：`calculate_reader_level`
- **函数类型**：纯业务函数
- **由谁调用**：阅读事件和 XP 查询
- **接收什么**：total_xp 整数。
- **返回什么**：level 整数。
- **内部顺序**：
  1. 确认 XP 不为负。
  2. 按明确规则计算，例如每 100 XP 升一级。
- **注意事项**：公式要单独测试；不要把计算复制在两个路由。

## 事件竞猜与预测市场

### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/events/{event_id}/bets`
- **后端函数**：`get_event_or_404`、`get_clock`、`get_open_event`、`RateLimiter.__call__`、`place_bet_in_memory`

### 后端依赖函数卡：`get_event_or_404`

#### 它解决的重复问题

事件详情、下注、编辑、关闭和结算都会先检查事件是否存在。该依赖把“读取路径 ID—查找事件—不存在时返回 404”集中在一个位置。

#### FastAPI 给它什么

路由路径里包含 `{event_id}` 时，FastAPI 会把解析后的整数 `event_id` 交给这个依赖函数。

#### 完整处理步骤

1. 接收 `event_id`。
2. 调用当前存储层的事件查找函数。内存阶段是遍历列表；数据库阶段会变成按主键查询。
3. 如果结果是 `None`，抛出 `HTTPException(404, "事件不存在")`。此时真正的路由函数不会执行。
4. 如果找到事件，返回事件对象。
5. FastAPI 将返回值注入路由参数，例如 `event = Depends(get_event_or_404)`。

#### 它不应该检查什么

这里不检查事件是否开放。原因是详情页允许查看已关闭和已结算事件。

“存在性”与“当前是否允许下注”是两条不同规则：

- `get_event_or_404`：只保证存在；
- `get_open_event`：在存在的基础上继续保证可下注。

---

## 后端子依赖卡：`get_open_event`

### 补充拆解

- **函数类型**：子依赖
- **由谁调用**：下注和试算等要求事件开放的路由
- **接收什么**：由 get_event_or_404 提供 event；由 get_clock 提供 now。
- **返回什么**：满足下注条件的事件。
- **内部顺序**：
  1. 确认 status 为 open。
  2. 确认 now 早于 deadline。
  3. 不满足时抛 409，分别使用 EVENT_NOT_OPEN 或 EVENT_DEADLINE_PASSED。
  4. 返回事件。
- **注意事项**：依赖只做前置检查，不扣积分、不创建 bet。


### 它依赖谁

它先依赖 `get_event_or_404`。

### 处理步骤

1. `get_event_or_404` 保证事件存在；
2. `get_open_event` 检查 `event["status"] == "open"`；
3. 不是 open 时抛 409；
4. 是 open 时返回事件。

### 哪些路由使用

- 下注；
- 修改仍开放的事件；
- 其他只允许开放状态的操作。

### 哪些路由不使用

- 查看已关闭事件详情；
- 管理员结算；
- 查询历史。

这说明依赖要按实际前置条件组合，不能把所有规则塞进一个“万能依赖”。

---


## 类依赖最小练习：`SimpleRateLimiter`

这项练习属于本阶段必做内容，但仍只是单进程教学实现，不能视为预测市场的“生产安全”方案。

### 目的

理解类实例如何保存配置：

- 最大请求次数；
- 时间窗口秒数。

### 初学版本可以更简单

不要一开始做复杂滑动窗口和代理 IP。可以按用户 ID 记录上次下注时间：

1. 获取用户 ID；
2. 查看上次请求时间；
3. 如果距离当前不足 1 秒，返回 429；
4. 否则更新上次时间并放行。

### 明确限制

- 数据在内存；
- 重启清空；
- 多进程不共享；
- 用户 ID 当前仍可伪造；
- 只是依赖类练习。

---

## 依赖重构后的下注接口

### 接口卡：`POST /api/v1/events/{event_id}/bets`

#### 路由现在直接获得什么

- 已确认存在且开放的 `event`；
- 已解析的 `BetCreate`；
- 可选的限流依赖结果。

#### 路由负责什么

只负责下注核心：

1. 查找选项；
2. 检查积分；
3. 修改奖池；
4. 创建回执；
5. 返回。

#### 为什么这更容易测试

状态检查和资源查找可以单独测试；下注函数不用每次构造各种不存在事件分支。

## 前端变化

没有 URL 或 JSON 变化。

你应该观察：重构后前端完全不用修改，说明后端公开契约稳定。


### 后端函数说明卡：`get_clock`
- **函数类型**：可覆盖依赖
- **由谁调用**：所有截止时间判断
- **接收什么**：无输入。
- **返回什么**：当前带时区 UTC datetime。
- **内部顺序**：
  1. 取得服务器当前 UTC 时间。
  2. 返回。
- **注意事项**：把时间封装后，测试可替换为固定时间；不要在多个函数中直接散落 now()。

### 后端函数说明卡：`RateLimiter.__call__`
- **函数类型**：可调用类实例依赖
- **由谁调用**：POST 下注路由；可为不同路由创建不同配置实例
- **接收什么**：客户端标识和当前时间。
- **返回什么**：通过时无业务返回值；超限时直接抛 429。
- **内部顺序**：
  1. 确定临时 client_key。阶段 6前可用 IP 与 Header 组合，但明确不可信。
  2. 删除窗口外的旧时间戳。
  3. 若剩余次数达到上限，计算等待秒数并抛 429。
  4. 否则记录当前时间并放行。
- **注意事项**：内存限流只适合单进程教学；要限制 key 数量并清理过期数据。

### 后端函数说明卡：`place_bet_in_memory`
- **函数类型**：纯业务函数
- **由谁调用**：place_bet 路由
- **接收什么**：开放事件、用户 ID、选项 ID、积分、幂等键。
- **返回什么**：BetReceipt。
- **内部顺序**：
  1. 确认选项归属。
  2. 检查幂等映射。
  3. 生成 bet_id。
  4. 创建下注记录。
  5. 更新池子。
  6. 保存幂等回执。
- **注意事项**：路由依赖已经检查事件开放，但业务函数仍应保持关键不变量，不能完全相信调用者。

## 阶段 5 验收

- 列表分页规则只定义一次。
- 所有文章详情/修改/删除都复用文章查找依赖。
- 下注依赖确保事件存在且开放。
- `yield` 后的代码在路由报错时仍执行。
- 前端真实请求没有因为内部重构而改变。

---

# 阶段 6：密码哈希、OAuth2 Password、JWT 与真实登录页面


## 进入条件

读完安全性全部章节。

## 两个项目共用的认证基础

### 本阶段施工清单

- **后端路由**：`POST /api/v1/auth/token`、`GET /api/v1/users/me`
- **后端函数**：`verify_password`、`authenticate_user`、`create_access_token`、`get_current_user`、`require_roles`

## 本阶段先掌握的四个函数

1. `verify_password`：验证明文密码和哈希；
2. `authenticate_user`：查用户并验证密码；
3. `create_access_token`：创建短期 JWT；
4. `get_current_user`：从请求中的 token 得到当前用户。

不要一开始同时实现刷新令牌、OAuth2 scopes、第三方登录、多设备会话和复杂 Cookie 策略。

---

## 用户数据最小形状

```json
{
  "id": 1,
  "username": "hazel",
  "password_hash": "...",
  "role": "admin",
  "is_active": true
}
```

前端永远不能得到 `password_hash`。

---

### 后端函数卡：`verify_password`

#### 补充拆解

- **函数类型**：纯安全函数
- **由谁调用**：authenticate_user
- **接收什么**：用户提交的明文密码和数据库/内存中的密码哈希。
- **返回什么**：布尔值。
- **内部顺序**：
  1. 调用官方教程当前推荐的密码哈希库进行验证。
  2. 返回验证结果。
- **注意事项**：不记录明文密码；不能用普通 SHA256直接存密码。


#### 输入

- 用户本次输入的明文密码；
- 数据库或内存中保存的密码哈希。

#### 输出

布尔值：匹配为真，不匹配为假。

#### 为什么不能直接保存明文密码

数据库泄漏时，明文密码会直接暴露。哈希设计为不能轻易还原原密码。

#### 这个函数不负责什么

- 不查用户；
- 不生成 token；
- 不返回 HTTP 响应。

保持职责单一。

---

### 后端函数卡：`authenticate_user`

#### 补充拆解

- **函数类型**：纯业务/安全函数
- **由谁调用**：登录路由
- **接收什么**：username、password。
- **返回什么**：认证成功的内部用户对象，失败返回空结果。
- **内部顺序**：
  1. 按 username 查用户。
  2. 用户不存在时仍执行一次 dummy hash，减少明显时间差。
  3. 验证密码。
  4. 检查 is_active。
  5. 成功返回用户。
- **注意事项**：对外错误统一为“用户名或密码错误”，不泄露账号是否存在。


#### 输入

用户名和明文密码。

#### 处理步骤

1. 根据用户名查用户；
2. 用户不存在，认证失败；
3. 调用 `verify_password`；
4. 密码不匹配，认证失败；
5. 用户被禁用，认证失败；
6. 成功时返回用户对象。

#### 为什么用户名不存在和密码错误最好返回相同外部提示

如果分别提示“用户不存在”和“密码错误”，攻击者可以枚举注册用户名。

前端统一显示“用户名或密码错误”。

日志内部可以记录更具体原因，但不能记录明文密码。

---

### 后端函数卡：`create_access_token`

#### 补充拆解

- **函数类型**：安全函数
- **由谁调用**：登录路由
- **接收什么**：user_id、过期时长和最少必要声明。
- **返回什么**：JWT 字符串。
- **内部顺序**：
  1. 构造 sub 为稳定用户 ID字符串。
  2. 加入 exp；可加入 role 但后续仍查当前用户。
  3. 使用配置中的固定算法和密钥签名。
- **注意事项**：JWT 是签名数据，不是加密容器；不能放密码或秘密。


#### 输入

当前用户的稳定标识，例如用户 ID 或用户名；过期时间。

#### 输出

JWT 字符串。

#### token 中可以放什么

- `sub`：用户标识；
- `exp`：过期时间；
- 可选的少量权限信息。

#### token 中不能放什么

- 密码；
- 密码哈希；
- 私钥；
- 机密业务数据。

JWT 的载荷通常可以被客户端查看，签名主要用于防篡改，不等于内容加密。

---

## 后端依赖卡：`get_current_user`

### 补充拆解

- **函数类型**：安全依赖
- **由谁调用**：所有需要登录的路由
- **接收什么**：OAuth2PasswordBearer 提取的 Bearer token。
- **返回什么**：当前公开/内部用户对象。
- **内部顺序**：
  1. 解码 token，固定允许算法。
  2. 检查 sub 和 exp。
  3. 用 sub 查当前用户。
  4. 检查用户仍存在且启用。
  5. 返回用户。
- **注意事项**：篡改、过期、缺 sub、用户不存在统一转 401，并带合适 WWW-Authenticate。


### 请求如何携带 token

请求头：

```text
Authorization: Bearer <token>
```

### 处理步骤

1. OAuth2 工具从请求头取出 Bearer token；
2. 解码并验证签名；
3. 检查过期时间；
4. 读取 `sub`；
5. 根据 `sub` 查用户；
6. 用户不存在或禁用时返回 401；
7. 成功时返回当前用户对象。

### 401 和 403 的区别

- 401：没有有效身份，例如 token 缺失、无效、过期；
- 403：身份有效，但没有执行该操作的权限。

---

### 接口卡：`POST /api/v1/auth/token`

#### 建议路由函数名

`login_for_access_token`

#### 为什么不是普通 JSON 登录

FastAPI 官方 OAuth2 Password 示例使用表单字段 `username` 和 `password`。这样 `/docs` 的 Authorize 流程能正常工作。

#### 输入

表单字段：

- `username`；
- `password`。

#### 处理步骤

1. 读取表单；
2. 调用 `authenticate_user`；
3. 失败返回 401；
4. 成功创建 token；
5. 返回 token 和类型。

#### 成功返回示例

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### 为什么返回 `token_type`

前端构造 Authorization 请求头时需要知道使用 Bearer 方案。

---

### 接口卡：`GET /api/v1/users/me`

#### 建议路由函数名

`read_current_user`

#### 依赖

`get_current_user`。

#### 功能

让前端在已有 token 时确认当前登录用户。

#### 成功返回

```json
{
  "id": 1,
  "username": "hazel",
  "role": "admin"
}
```

不返回密码哈希。

---

### 后端函数说明卡：`require_roles`
- **函数类型**：参数化授权依赖或简单子依赖
- **由谁调用**：作者/管理员写操作
- **接收什么**：当前用户与允许角色集合。
- **返回什么**：通过时返回当前用户；不通过抛 403。
- **内部顺序**：
  1. 先由 get_current_user 完成认证。
  2. 检查 role 是否允许。
  3. 返回用户。
- **注意事项**：401表示不知道是谁；403表示已经登录但没有权限。

## 博客权限规则
### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/posts`、`PATCH /api/v1/posts/{post_id}（权限升级）`、`POST /api/v1/posts/{post_id}/publish`
- **后端函数**：本阶段没有新增独立后端函数。


- 所有人可以 GET 已发布文章；
- 登录作者可以创建文章；
- 文章作者或管理员可以修改自己的文章；
- 管理员可以删除任意文章；
- 当前用户来自 token，不再来自请求体中的作者 ID。

### 接口卡：`POST /api/v1/posts`（认证升级）

#### 与旧版的变化

请求体不再允许自由填写可信作者身份。

处理流程：

1. `get_current_user` 验证 token；
2. 读取标题和正文；
3. 作者 ID 使用当前用户 ID；
4. 创建文章；
5. 返回 201。

显示用作者名可以从当前用户得到。

#### 为什么不能相信前端提交的 `author_id`

用户可以修改请求体，把自己伪装成其他作者。

身份必须来自已验证 token。

---

### 接口说明卡：`PATCH /api/v1/posts/{post_id}（权限升级）`
- **建议路由函数名**：`update_post`。
- **这个后端功能可以做什么**：文章作者可以改自己的文章，admin可以改任何文章。
- **输入从哪里来**：路径、PostUpdate body、current_user。
- **路由函数的核心职责**：先认证，再检查资源所有权，最后更新。
- **处理顺序**：
  1. 得到文章。
  2. 得到当前用户。
  3. 若不是 admin且 user_id != article.author_id，抛 403。
  4. 执行阶段 4更新流程。
- **成功返回**：200，返回详情。
- **失败返回**：401、403、404、409、422。
- **前端拿到结果后做什么**：非作者看到按钮可以隐藏，但即使手工请求也会被后端拒绝。
- **本阶段仍然存在的限制**：role 是简单字符串，细粒度权限到阶段 12。

### 接口说明卡：`POST /api/v1/posts/{post_id}/publish`
- **建议路由函数名**：`publish_post`。
- **这个后端功能可以做什么**：把作者草稿发布为公开文章。
- **输入从哪里来**：路径 post_id；current_user；无请求体或可选发布说明。
- **路由函数的核心职责**：检查所有权和当前状态，执行 draft → published。
- **处理顺序**：
  1. 查文章。
  2. 认证与所有权检查。
  3. 确认 status=draft。
  4. 确认标题和正文满足发布要求。
  5. 设置 status=published、published_at。
  6. 返回。
- **成功返回**：200，返回 PostDetail。
- **失败返回**：401、403、404；已经发布或已删除 409。
- **前端拿到结果后做什么**：编辑页“发布”按钮成功后显示公开状态。
- **本阶段仍然存在的限制**：阶段 10才加入发布事件和后台通知。

## 预测市场权限规则
### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/events/{event_id}/bets`、`POST /api/v1/admin/events`、`POST /api/v1/admin/events/{event_id}/close`、`POST /api/v1/admin/events/{event_id}/settle`
- **后端函数**：本阶段没有新增独立后端函数。


- 普通用户可以查看事件；
- 登录用户可以下注；
- 管理员可以创建、关闭、取消和结算事件；
- `BetCreate` 删除 `user_id` 字段；
- 下注用户由 `get_current_user` 得到。

### 接口卡：`POST /api/v1/events/{event_id}/bets`（认证升级）

#### 变化

前端请求体只需要：

```json
{
  "option_id": 2,
  "amount_points": 20
}
```

后端把当前用户 ID 写入下注回执。

#### 处理步骤

1. 验证当前用户；
2. 确认事件开放；
3. 查选项；
4. 检查积分；
5. 创建下注；
6. 返回回执。

当前仍没有持久余额，数据库阶段加入。

---

### 接口说明卡：`POST /api/v1/admin/events`
- **建议路由函数名**：`create_event_as_admin`。
- **这个后端功能可以做什么**：只有管理员可以创建事件。
- **输入从哪里来**：EventCreate body；current_user。
- **路由函数的核心职责**：检查 admin角色，再调用 create_event。
- **处理顺序**：
  1. 认证。
  2. 角色检查 admin。
  3. 验证事件。
  4. 创建并返回。
- **成功返回**：201，返回 EventPublicDetail。
- **失败返回**：401、403、422、409。
- **前端拿到结果后做什么**：管理页面显示创建表单；普通用户不显示，但后端权限才是真正防线。
- **本阶段仍然存在的限制**：权限仍是角色级。

### 接口说明卡：`POST /api/v1/admin/events/{event_id}/close`
- **建议路由函数名**：`close_event_as_admin`。
- **这个后端功能可以做什么**：管理员关闭事件。
- **输入从哪里来**：路径 event_id；current_user。
- **路由函数的核心职责**：授权后调用状态机。
- **处理顺序**：
  1. 认证。
  2. 检查 admin。
  3. 查事件。
  4. open → closed。
- **成功返回**：200，返回状态转换结果。
- **失败返回**：401、403、404、409。
- **前端拿到结果后做什么**：管理页面二次确认后调用；用户页面重新加载状态。
- **本阶段仍然存在的限制**：无审计数据库。

### 接口说明卡：`POST /api/v1/admin/events/{event_id}/settle`
- **建议路由函数名**：`settle_event`。
- **这个后端功能可以做什么**：管理员指定获胜选项并完成教学版内存结算。
- **输入从哪里来**：路径 event_id；JSON body winning_option_id；current_user。
- **路由函数的核心职责**：只允许 closed事件结算；验证获胜选项属于事件；阶段 6只标记结果，不做真实余额分配。
- **处理顺序**：
  1. 认证和 admin授权。
  2. 查事件。
  3. 确认 status=closed。
  4. 确认 winning_option_id属于事件。
  5. 设置 winning_option_id、status=settled、settled_at。
  6. 返回结算摘要。
- **成功返回**：200，返回 event_id、status=settled、winning_option_id、settled_at。
- **失败返回**：401、403、404、409、422。
- **前端拿到结果后做什么**：管理页面显示不可逆提示；成功后刷新事件详情。
- **本阶段仍然存在的限制**：真正的账本和收益分配到阶段 8事务中完成。

## 前端登录最小 HTML

```html
<form id="login-form">
  <input id="username-input" placeholder="用户名" required>
  <input id="password-input" type="password" placeholder="密码" required>
  <button type="submit">登录</button>
</form>
<p id="login-message"></p>
<button id="logout-button">退出登录</button>
```

## 前端状态变量

```text
accessToken = null
currentUser = null
```

初学阶段先放内存变量。刷新页面后需要重新登录，这反而便于理解 token 如何驱动请求。

本阶段使用 `sessionStorage` 在当前标签页保存 token；关闭标签页后自动清除。暂时不要加入复杂的持久登录。

### 前端函数卡：`handleLoginSubmit`

#### 为什么使用 `URLSearchParams` 或 `FormData`

OAuth2 Password 登录端点接收表单，不是 JSON。

#### 处理步骤

1. 阻止表单刷新；
2. 读取用户名密码；
3. 创建表单数据；
4. POST 到 `/auth/token`；
5. 登录失败显示统一提示；
6. 成功时保存 `data.access_token`；
7. 调用 `loadCurrentUser()`；
8. 根据用户角色显示或启用管理按钮。

#### 安全注意

- 不打印密码；
- 不把密码存到变量以外的长期存储；
- 不把 token 写在 URL；
- “隐藏按钮”不是后端授权，只是界面优化。

### 前端函数卡：`authorizedFetch`

前期可以先不抽这个函数，每个受保护请求手动添加请求头，帮助理解：

```text
Authorization: Bearer ${accessToken}
```

当重复三次以上，再抽取公共函数。

公共函数职责：

1. 接收 URL 和普通 fetch 配置；
2. 复制 headers；
3. 如果有 token，加入 Authorization；
4. 调用 fetch；
5. 返回 Response。

不要在公共函数里自动把所有错误吞掉，否则具体页面不知道发生了什么。

### 前端函数卡：`loadCurrentUser`

1. 使用 token 请求 `/users/me`；
2. 401 时清空 token 和用户；
3. 成功时保存当前用户；
4. 页面显示用户名和角色。

### 前端函数卡：`logout`

1. 把 `accessToken` 设为 `null`；
2. 把 `currentUser` 设为 `null`；
3. 清除可选的 sessionStorage；
4. 更新页面按钮状态。

JWT 的客户端退出本质是删除本地凭证。服务端即时吊销需要额外会话或黑名单机制，属于进阶内容。


## 阶段 6 验收

- 密码只保存哈希。
- 登录错误不泄漏用户名是否存在。
- token 中没有密码或秘密。
- 写操作身份来自 token。
- 未登录下注返回 401。
- 普通用户调用管理员接口返回 403。
- 前端真实登录后，创建文章和下注都携带 Bearer token。

---
# 阶段 7：正式理解 CORS、中间件与整理公共 fetch


## 进入条件

读完：

- 中间件；
- CORS。

## 两个项目共用的 CORS 与中间件能力

### 本阶段施工清单

- **后端路由**：`GET /api/v1/debug/request-context`
- **后端函数**：`add_request_context`、`request_id_middleware`、`request_timing_middleware`

## 为什么阶段 0 已经用了 CORS，现在才正式学

阶段 0 的目标是让前后端从第一天连通，因此先使用最小固定配置。

现在你已经经历：

- GET；
- POST JSON；
- PATCH；
- DELETE；
- multipart 文件上传；
- Authorization 请求头。

此时再系统理解 CORS，会知道每个配置究竟在帮助哪种真实请求，而不是只背参数。

---

## 7.1 “源”到底是什么

一个源由三部分组成：

1. 协议；
2. 主机；
3. 端口。

这些地址是不同源：

```text
http://127.0.0.1:5500
http://127.0.0.1:8000
http://localhost:5500
```

即使都指向本机，主机字符串或端口不同，浏览器仍可能视为不同源。

## 7.2 为什么 `/docs` 能调用，前端却可能被 CORS 拦截

`/docs` 页面由后端自己提供，通常与 API 同源。

你的前端来自 5500 端口，是另一个源。浏览器会额外执行 CORS 检查。

CORS 是浏览器限制。使用命令行工具请求 API 时，通常不会受到浏览器同源策略限制。

## 7.3 预检请求是什么

浏览器在某些跨域请求前，会先自动发送 `OPTIONS` 请求询问后端：

- 是否允许这个前端源；
- 是否允许 POST/PATCH/DELETE；
- 是否允许 `Authorization`、`Content-Type` 等请求头。

这叫预检请求。

你的 JavaScript 不需要手动发送 OPTIONS。CORS 中间件负责回答。

## 7.4 本项目 CORS 配置怎样逐项决定

### `allow_origins`

只列出实际前端地址。

开发阶段通常是：

- `http://127.0.0.1:5500`；
- `http://localhost:5500`。

### `allow_methods`

项目会使用 GET、POST、PATCH、DELETE，因此允许这些方法。

学习阶段写 `*` 可以减少配置负担，但应理解它表示所有方法。更严格时列出实际方法。

### `allow_headers`

项目会发送：

- `Content-Type`；
- `Authorization`；
- 可选 `X-Client-Name`。

### `allow_credentials`

只有要跨域发送 Cookie 等凭证时才需要。当前 JWT 放在 Authorization 头，不必为了“看起来完整”随意开启。

### CORS 不做什么

CORS 不验证用户身份，不限制命令行攻击者，也不代替 JWT 权限。

---

# 7.5 中间件：每个请求都经过的外层函数

### 中间件函数卡：`add_request_context`

#### 这个函数可以做什么

为每个请求记录：

- 方法；
- 路径；
- 状态码；
- 处理耗时。

可以在请求前执行一段逻辑，在路由完成后再执行一段逻辑。

#### 输入

- `request`：当前请求；
- `call_next`：把请求交给后续路由的函数。

#### 详细处理步骤

1. 记录开始时间。
2. 从请求读取方法，例如 GET。
3. 读取路径，例如 `/api/v1/posts`。
4. 调用 `await call_next(request)`。
5. 等待路由和依赖完成，得到 response。
6. 计算耗时。
7. 打印方法、路径、状态码和耗时。
8. 返回 response。

#### 为什么一定要返回 response

中间件拿到后端生成的响应后，如果不返回，客户端收不到结果。

#### 异常时怎么办

可以用 `try/finally` 确保耗时记录执行，但不要在初学阶段随意捕获所有异常并改成 200。

异常应该继续交给 FastAPI 的异常处理系统。

#### 为什么不把完整请求体写日志

请求体可能包含密码、token、文章内容或隐私数据。日志应记录必要元数据，不记录秘密。

---

### 后端函数卡：`request_id_middleware`

**函数类型：** HTTP 中间件

**由谁调用：** 所有 HTTP 请求

**接收什么：** Request、call_next。

**返回什么：** Response。

**内部处理顺序：**

1. 读取可选 X-Request-Id并检查长度。
2. 没有时生成。
3. 写入 request.state。
4. await call_next。
5. 写入响应 Header。

**为什么要单独写这个函数：** 日志和前端错误需要同一编号。

**重点语法或方法：** `@app.middleware('http')`、request.state、headers。

**边界与限制：** 请求 ID不是身份和幂等键。

### 后端函数卡：`request_timing_middleware`

**函数类型：** HTTP 中间件

**由谁调用：** 所有 HTTP 请求

**接收什么：** Request、call_next。

**返回什么：** Response。

**内部处理顺序：**

1. 记录 perf_counter 起点。
2. await 下游。
3. 计算毫秒。
4. 记录 method/path/status/request_id。

**为什么要单独写这个函数：** 避免每个路由复制计时代码。

**重点语法或方法：** `time.perf_counter()`、try/finally。

**边界与限制：** 日志中不写敏感 query/header。

### 接口卡：`GET /api/v1/debug/request-context`

**建议路由函数名：** `get_request_context`

**用户从页面上做什么：** 开发页面点击“检查请求上下文”。

**这个功能为什么值得在本阶段加入：** 验证中间件确实写入 request state 与响应 Header。

**输入来自哪里：** Request；可选 X-Client-Version。

**后端必须按下面顺序处理：**

1. 从 request.state 读 request_id。
2. 读取 method/path/client version。
3. 只返回安全字段。
4. 生产环境不注册或返回 404。

**成功时返回什么：** 200，request_id、method、path、client_version。

**可能失败的情况：** 非开发环境不可用。

**前端怎样调用和更新页面：** apiRequest 读取 X-Request-Id，错误时显示编号。

**本功能重点函数或语法：** 直接 Request、环境开关。

**本阶段仍然没有解决什么：** 不属于业务接口。

# 7.6 为什么此时才拆出 `api.js`

前面只有少量请求，放一个 `main.js` 更容易理解。

现在有：

- 登录；
- 列表；
- 详情；
- 创建；
- 修改；
- 删除；
- 上传；
- 下注；
- 管理操作。

重复的基础 URL、token 请求头和错误读取开始变多，此时拆出一个 `api.js` 有明确价值。

建议前端目录：

```text
frontend/
├── index.html
└── scripts/
    ├── api.js
    └── main.js
```

`api.js` 只处理 HTTP。

`main.js` 只处理页面元素、用户事件和渲染。

---

### 前端函数卡：`apiRequest`

#### 输入

- `path`：例如 `/api/v1/posts`；
- `options`：可选 fetch 配置，例如 method、headers、body；
- `needAuth`：是否需要 token。

#### 处理步骤

1. 把固定后端基础地址和 path 拼接。
2. 创建新的 headers 对象，避免直接修改调用者对象。
3. 如果 `needAuth` 为真且有 token，加入 Authorization。
4. 调用 fetch。
5. 尝试读取 JSON。
6. 如果 `response.ok` 为假，创建一个包含状态码和后端 detail 的错误。
7. 成功时返回解析后的数据。

#### 为什么“尝试读取 JSON”

有些响应可能没有 JSON，例如未来的 204 或文件下载。核心 JSON 接口可以先默认读取，后续高级响应时再扩展。

#### 为什么不在这里直接操作 DOM

`api.js` 不知道错误应该显示在登录区、文章区还是下注区。

它只返回数据或抛出错误，由页面函数决定显示位置。

#### 为什么不自动重试所有 POST

POST 可能创建资源或下注。自动重试可能重复执行。

初学阶段只对 GET 考虑手动重试，不做隐藏自动重试。

---

### 前端函数卡：`showMessage`

#### 输入

- 要显示的文本；
- 可选目标元素。

#### 作用

统一使用 `textContent` 写消息，避免每个函数重复三四行。

#### 不要做什么

不要把任意后端字符串放进 `innerHTML`。

---

### 前端函数卡：`setButtonLoading`

#### 输入

- 按钮；
- 是否加载中。

#### 处理逻辑

加载开始：

- 禁用按钮；
- 保存原文字；
- 显示“处理中……”。

请求结束：

- 恢复文字；
- 恢复可用。

#### 为什么有实际价值

防止用户连续点击创建文章或下注，减少重复请求。

这不是后端幂等或事务替代品。后端仍需保证安全。

---

## 本阶段博客前端整理

### `loadPosts`

改为调用 `apiRequest`，其余分页和 DOM 逻辑不变。

### `handlePostSubmit`

- 负责读取和检查表单；
- 调用 apiRequest；
- 成功后刷新；
- `finally` 中恢复按钮。

### `handleImportSubmit`

FormData 请求不能自动添加 JSON Content-Type。`apiRequest` 必须允许调用者传 FormData，并且此时不要设置 `application/json`。

---

## 本阶段预测市场前端整理

### `handleBet`

- 读取选项和积分；
- 调用受保护 apiRequest；
- 显示下注回执；
- 刷新事件详情。

### 401 的统一处理

如果后端返回 401：

1. 清除 token；
2. 清除当前用户；
3. 显示“登录已失效，请重新登录”；
4. 不继续执行成功操作。

### 403 的处理

身份仍有效，不应自动退出。显示“当前账号没有权限”。

---


## 阶段 7 验收

- 能解释端口不同就是不同源。
- 能说明 CORS 不等于认证。
- Authorization 请求头可以跨域发送。
- 中间件打印请求信息但不记录密码或 token。
- `api.js` 不操作 DOM。
- `main.js` 不重复拼后端基础地址。
- 所有业务页面仍使用真实后端数据。

---

# 阶段 8：SQLModel、数据库持久化与后端文件拆分


## 进入条件

读完：

- SQL（关系型）数据库；
- 更大的应用——多个文件。

## 为什么现在才加入数据库

前面你已经掌握：

- API 路由；
- 请求模型；
- 响应模型；
- 错误；
- 依赖；
- 登录；
- 真实前端。

现在把内存存储换成数据库时，你能清楚看到“业务接口不变，数据来源改变”。

## 本阶段数据库选择

先跟随 FastAPI 官方教程使用 SQLModel 和 SQLite。

核心项目使用同步 `Session`，路由可以使用普通 `def`。不要同时学习异步 SQLAlchemy、asyncpg、连接池调优和复杂 repository 模式。

生产扩展再讨论 PostgreSQL。

---

## 两个项目共用的数据库基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`get_session`

# 8.1 后端目录逐步拆分

博客：

```text
backend/app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── dependencies.py
├── services.py
└── routers/
    ├── auth.py
    └── posts.py
```

预测市场类似，增加 `events.py` 和 `bets.py`。

## 每个文件干什么

### `main.py`

- 创建 FastAPI；
- 配置 CORS 和中间件；
- 注册路由；
- 不堆具体 CRUD。

### `database.py`

- 创建 engine；
- 提供建表和 Session 配置。

### `models.py`

- SQLModel table 模型；
- 表字段和外键。

### `schemas.py`

- 请求和响应模型；
- 不直接执行 SQL。

### `dependencies.py`

- `get_session`；
- `get_current_user`；
- 资源查找依赖。

### `services.py`

- 创建文章；
- 下注；
- 结算等业务流程。

### `routers/`

- HTTP 路径；
- 调用依赖和 service；
- 返回响应。

### 为什么不急着创建 repositories

当前 SQL 很简单。再加一层可能只是把 `session.exec()` 从一个文件搬到另一个文件。

等数据访问逻辑真的复杂或需要替换存储时再创建。

---

### 后端依赖函数卡：`get_session`

#### 目的

每个请求需要一个数据库会话，用来查询、添加、提交或回滚。

#### 处理步骤

1. 创建 Session；
2. `yield` 给路由或 service；
3. 请求结束后关闭 Session。

#### 为什么不能全局共享一个 Session

Session 保存当前事务和对象状态。全局共享会让多个请求互相污染，并产生并发问题。

#### `yield` 后为什么必须关闭

不关闭会持续占用数据库连接或资源。

---

# 8.2 博客数据库模型
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts`、`GET /api/v1/posts/{post_id}`、`POST /api/v1/posts`、`PATCH /api/v1/posts/{post_id}`、`DELETE /api/v1/posts/{post_id}`、`GET /api/v1/posts/{post_id}/comments`、`POST /api/v1/posts/{post_id}/comments`、`GET /api/v1/tags`
- **后端函数**：`create_post_service`


## `User` 表

最少字段：

- `id`；
- `username`，唯一；
- `password_hash`；
- `role`；
- `is_active`。

## `Post` 表

最少字段：

- `id`；
- `title`；
- `content`；
- `author_id`，关联 User；
- `is_published`；
- `created_at`；
- `updated_at`。

## `Comment` 表

- `id`；
- `post_id`；
- `author_id`；
- `content`；
- `created_at`。

不要一开始加入点赞、多级回复、审核树、全文搜索和附件表。

---

### 接口卡：`GET /api/v1/posts`（数据库版）

#### URL 和前端是否变化

不变化。

前端仍然请求相同 URL，仍然收到 `items/total/skip/limit`。

#### 后端处理步骤

1. 接收搜索和分页条件。
2. 构造数据库查询条件。
3. 只查询已发布文章，除非管理员页面明确需要草稿。
4. 如果有 keyword，使用数据库的包含条件。
5. 查询符合条件的总数量。
6. 按 ID 或创建时间排序。
7. 使用 offset 和 limit 取当前页。
8. 转换成摘要响应。
9. 返回。

#### `skip` 在 SQL 中对应什么

SQLModel/SQLAlchemy 查询中通常使用 `offset(skip)`。

它与内存切片的“跳过前 N 条”含义相同。

#### `limit` 对应什么

查询的 `limit(limit)`，让数据库最多返回 N 行。

#### 为什么不能先把整张表查进 Python 再切片

数据库应负责筛选和分页，否则数据量大时：

- 浪费内存；
- 浪费数据库到应用的传输；
- 响应变慢。

#### `total` 怎么来

需要一条计数查询，计算符合筛选条件的总行数。

不能使用当前页 `len(items)` 代替。

---

### 接口卡：`GET /api/v1/posts/{post_id}`（数据库版）

#### 处理步骤

1. 使用 Session 按主键查询。
2. 不存在抛 404。
3. 未发布文章：
   - 作者或管理员可以看；
   - 普通访客按项目规则返回 404 或 403。
4. 返回详情响应模型。

#### 为什么可能对草稿返回 404

向未授权用户返回 404，可以不暴露草稿是否存在。规则要全项目一致。

---

### 接口卡：`POST /api/v1/posts`（数据库版）

#### 处理步骤

1. 验证当前用户；
2. 验证请求字段；
3. 创建 Post 表对象；
4. `author_id` 使用当前用户 ID；
5. `session.add(post)`；
6. `session.commit()`；
7. `session.refresh(post)`；
8. 返回 201。

#### `commit` 做什么

把事务中的修改真正提交到数据库。

#### `refresh` 做什么

数据库可能生成 ID 或默认值。refresh 让 Python 对象重新读取这些数据库结果。

#### 提交失败怎么办

使用异常处理并执行 rollback，确保 Session 回到可用状态。

不要把数据库内部错误原样返回给前端，避免泄漏表名或 SQL。

---

### 后端 service 函数卡：`create_post_service`

#### 补充拆解

**函数类型：** 数据库业务函数

**由谁调用：** POST 文章和 Markdown 导入

**接收什么：** Session、当前作者、PostCreate。

**返回什么：** 已 commit/refresh 的 Post。

**内部处理顺序：**

1. 清理并检查冲突。
2. 构造表模型并 add。
3. commit。
4. refresh 获取 ID。
5. 异常 rollback。

**为什么要单独写这个函数：** 两个创建入口复用同一事务逻辑。

**重点语法或方法：** `session.add/commit/refresh/rollback`。

**边界与限制：** 返回业务对象，不返回 Response。


#### 输入

- Session；
- 当前用户；
- 已验证的创建数据。

#### 处理步骤

1. 清理业务字段；
2. 如有唯一 slug，检查冲突；
3. 创建数据库对象；
4. 添加并提交；
5. 刷新；
6. 返回对象。

#### 路由负责什么

- HTTP 输入和状态码；
- 调用 service；
- 返回响应。

#### service 负责什么

- 业务规则；
- 数据库事务步骤。

---

### 接口卡：`PATCH /api/v1/posts/{post_id}`（数据库版）

#### 处理步骤

1. 查询文章；
2. 检查当前用户是作者或管理员；
3. 取得实际提交字段；
4. 清理和验证；
5. 更新字段；
6. 更新 `updated_at`；
7. commit；
8. refresh；
9. 返回详情。

#### 权限失败为什么是 403

文章存在，用户也已登录，但没有修改权限。

---

### 接口卡：`DELETE /api/v1/posts/{post_id}`（数据库版）

初学阶段可使用真正删除：

1. 查询文章；
2. 检查权限；
3. 删除；
4. commit；
5. 返回确认。

软删除是扩展，不必一开始加入 `deleted_at` 和复杂过滤。

---

### 接口卡：`GET /api/v1/posts/{post_id}/comments`

#### 功能

加载某篇文章的评论。

#### 处理步骤

1. 确认文章可访问；
2. 查询 `post_id` 匹配的评论；
3. 按创建时间升序或降序，规则固定；
4. 分页；
5. 返回评论摘要。

#### 前端做什么

点击文章后，在正文下面调用评论接口，创建普通段落显示用户名和内容。

### 接口卡：`POST /api/v1/posts/{post_id}/comments`

#### 输入

JSON：`content`。

#### 处理步骤

1. 验证当前用户；
2. 确认文章存在且已发布；
3. 清理评论；
4. 检查非空和长度；
5. 创建 Comment；
6. commit；
7. 返回 201。

#### 前端做什么

成功后清空评论输入框，重新加载评论列表。

---

### 接口卡：`GET /api/v1/tags`

**建议路由函数名：** `list_tags`

**用户从页面上做什么：** 页面加载标签筛选。

**这个功能为什么值得在本阶段加入：** 文章已经有 tags，但前端不应靠猜字符串；数据库可提供标签及文章数量。

**输入来自哪里：** 可选 keyword query。

**后端必须按下面顺序处理：**

1. 查询已发布文章。
2. 收集并规范化标签。
3. 统计每个标签的文章数量。
4. 排序并返回。

**成功时返回什么：** 200，`items=[{name, post_count}]`。

**可能失败的情况：** query 422；无标签返回空列表。

**前端怎样调用和更新页面：** 前端创建最简单的 select 或按钮，选择后复用文章查询。

**本功能重点函数或语法：** 字典计数；后期可规范化标签关联表。

**本阶段仍然没有解决什么：** 当前 JSON 标签字段不适合复杂搜索。

# 8.3 预测市场数据库模型
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/users/me/balance`、`POST /api/v1/events/{event_id}/bets`、`GET /api/v1/users/me/bets`、`GET /api/v1/users/me/ledger`、`POST /api/v1/admin/events/{event_id}/settle`、`POST /api/v1/admin/events/{event_id}/refund`、`GET /api/v1/users/me/positions`
- **后端函数**：`place_bet_service`、`settle_event_service`


## `Event` 表

- `id`；
- `question`；
- `status`；
- `winning_option_id`，可空；
- `created_by`；
- `created_at`。

## `Option` 表

- `id`；
- `event_id`；
- `text`；
- `pool_points`。

## `User` 表

增加：

- `balance_points`。

## `Bet` 表

- `id`；
- `user_id`；
- `event_id`；
- `option_id`；
- `amount_points`；
- `created_at`。

## `LedgerEntry` 表

- `id`；
- `user_id`；
- `change_points`，可正可负；
- `reason`；
- `related_bet_id`；
- `created_at`。

### 为什么需要账本

只改余额后，不知道余额为什么变化。

账本记录每次增减，便于排查：

- 下注扣除；
- 结算奖励；
- 取消退款。

学习阶段账本不需要复杂会计系统，但不能省略变化原因。

---

### 接口卡：`GET /api/v1/users/me/balance`

#### 功能

前端显示当前登录用户的余额。

#### 处理步骤

1. 验证当前用户；
2. 从数据库读取最新用户；
3. 返回用户 ID 和 `balance_points`。

#### 成功返回

```json
{
  "user_id": 7,
  "balance_points": 980
}
```

#### 为什么每次从后端读

前端显示的余额可能过时。后端数据库才是真实来源。

---

### 接口卡：`POST /api/v1/events/{event_id}/bets`（数据库事务版）

#### 这一版和内存版最大的变化

必须同时完成：

- 扣用户余额；
- 创建 Bet；
- 写 LedgerEntry；
- 增加选项奖池。

这四项要么全部成功，要么全部失败。

#### 详细处理顺序

1. 验证当前用户；
2. 查询开放事件；
3. 查询属于该事件的选项；
4. 检查积分为正整数；
5. 读取用户最新余额；
6. 检查余额是否足够；
7. 从用户余额减去下注积分；
8. 创建 Bet；
9. 增加 Option.pool_points；
10. 创建负数账本记录；
11. commit 整个事务；
12. refresh 必要对象；
13. 返回下注回执和新余额。

#### 修改数据之前的最后一道线

前六步都是检查。只有全部通过，才从第七步开始修改。

#### 成功返回示例

```json
{
  "bet": {
    "id": 31,
    "event_id": 4,
    "option_id": 9,
    "amount_points": 20
  },
  "balance_points": 980,
  "option_pool_points": 240
}
```

#### 为什么返回新余额

前端可以立即更新余额显示。

仍建议在关键操作后调用余额接口校准。

#### 失败时必须保证什么

余额不足时：

- 不创建 Bet；
- 不写账本；
- 不增加奖池；
- 余额不变。

数据库异常时也不能只完成其中一半。

#### SQLite 并发限制

这个简单事务适合学习和低并发本地运行，但不是高并发资金系统的最终方案。

不要在 SQLite 上假装使用 PostgreSQL 行锁。生产并发控制作为进阶讨论。

---

### 后端 service 函数卡：`place_bet_service`

#### 补充拆解

- **函数类型**：核心事务service
- **由谁调用**：下注路由
- **接收什么**：Session、user_id、event_id、option_id、amount_points、idempotency_key、now。
- **返回什么**：BetReceipt和replayed标志。
- **内部顺序**：
  1. 查询同用户幂等键。若存在且请求摘要一致，返回旧回执；不同则409。
  2. 读取事件，检查open和deadline。
  3. 验证选项归属。
  4. 执行条件原子扣减：只有balance_points >= amount_points才更新。
  5. 检查受影响行数；0表示余额不足。
  6. 插入bet。
  7. 插入ledger_entry，change_points为负。
  8. 更新option.pool_points。
  9. commit；任何一步失败rollback。
  10. 构造回执。
- **注意事项**：SQLite上不要把with_for_update当真实行锁；条件UPDATE和唯一约束是本阶段重点。


#### 输入

- Session；
- 当前用户 ID；
- 事件 ID；
- 选项 ID；
- 积分。

#### 输出

包含 Bet、新余额和奖池的结果对象。

#### 为什么 route 不直接写全部事务

下注有多条业务规则。独立 service：

- 更容易测试；
- 管理员代操作或未来任务也能复用；
- HTTP 路由更短。

#### 异常处理原则

service 可以抛明确业务异常，由路由或全局异常处理器转换成 404、409 等。

不要在深层 service 直接操作 DOM 或前端消息。

---

### 接口卡：`GET /api/v1/users/me/bets`

#### 功能

用户查看自己的下注历史。

#### 输入

分页参数，可选事件状态。

#### 处理步骤

1. 验证当前用户；
2. 查询 `user_id` 等于当前用户的 Bet；
3. 关联需要显示的事件问题和选项文字；
4. 排序分页；
5. 返回。

#### 安全要求

不能让用户通过查询参数改成其他 `user_id` 查看他人记录。

---

### 接口卡：`GET /api/v1/users/me/ledger`

#### 功能

显示余额变化记录。

#### 返回字段

- 变化积分；
- 原因；
- 关联下注 ID；
- 时间。

前端对负数显示“扣除”，正数显示“增加”。无需 CSS。

---

### 接口卡：`POST /api/v1/admin/events/{event_id}/settle`

#### 前置条件

- 当前用户是管理员；
- 事件状态为 closed；
- 获胜选项属于该事件；
- 事件没有结算过。

#### 简化结算规则

为了控制难度，可以采用简单规则：

- 押中者退还本金，并获得与本金相同的奖励；
- 即返回 `amount_points * 2`；
- 未押中者不返还。

这不是实际预测市场定价，只是事务练习。

#### 处理步骤

1. 查询并锁定当前业务流程所需数据；SQLite 学习版只在一个事务中顺序处理。
2. 验证事件状态。
3. 验证获胜选项。
4. 查询该选项全部下注。
5. 对每笔获胜下注计算返还。
6. 更新对应用户余额。
7. 为每笔返还写账本。
8. 设置事件 `winning_option_id`。
9. 设置状态 `settled`。
10. commit。
11. 返回结算摘要。

#### 成功返回示例

```json
{
  "event_id": 4,
  "status": "settled",
  "winning_option_id": 9,
  "winner_count": 3,
  "total_paid_points": 160
}
```

#### 为什么不返回每个用户完整私密数据

管理员只需要结算摘要。详细账本可在内部查询，避免巨大响应和隐私泄漏。

---

### 接口卡：`POST /api/v1/admin/events/{event_id}/refund`

#### 功能

取消事件后，把每笔下注本金退还用户。

#### 处理步骤

1. 管理员认证；
2. 事件必须 cancelled；
3. 检查未退款；
4. 查询所有下注；
5. 给每个用户增加原下注积分；
6. 写退款账本；
7. 标记事件已退款或标记每笔 Bet；
8. commit；
9. 返回退款摘要。

#### 为什么必须有“是否已经退款”标记

管理员重复点击不能重复加钱。

这就是幂等性最直观的业务例子。

---

### 接口卡：`GET /api/v1/users/me/positions`

**建议路由函数名：** `list_my_positions`

**用户从页面上做什么：** 点击“我的持仓”。

**这个功能为什么值得在本阶段加入：** 下注列表是明细，持仓是按事件与选项汇总，能练习数据库聚合。

**输入来自哪里：** Bearer token；可选 status query。

**后端必须按下面顺序处理：**

1. 查询当前用户 bets。
2. 按 `(event_id, option_id)` 分组。
3. 累加积分并计数。
4. 补充事件问题和选项文字。
5. 返回汇总。

**成功时返回什么：** 200，持仓列表。

**可能失败的情况：** 401、query 422。

**前端怎样调用和更新页面：** 个人中心用若干 `<p>` 或 Vue 列表显示，不做图表。

**本功能重点函数或语法：** 复合键聚合、sum/count。

**本阶段仍然没有解决什么：** 结算前不计算收益。

### 后端函数卡：`settle_event_service`

**函数类型：** 数据库事务函数

**由谁调用：** 管理员结算路由

**接收什么：** Session、event、winning_option_id、admin。

**返回什么：** SettlementSummary。

**内部处理顺序：**

1. 验证状态和幂等。
2. 查询未处理下注。
3. 计算整数派奖。
4. 写账本、余额和 bet 状态。
5. 更新事件。
6. 一次 commit；失败 rollback。

**为什么要单独写这个函数：** 结算必须同成同败，不能循环内多次 commit。

**重点语法或方法：** 事务、整数余数规则、唯一约束。

**边界与限制：** 大量结算以后需要任务队列。

## 数据库阶段前端变化

URL 和主要 JSON 契约尽量不变。

新增：

- 登录后加载余额；
- 下注成功更新余额；
- “我的下注”按钮；
- “余额记录”按钮；
- 管理员结算表单。

HTML 仍然可以只使用按钮、段落、输入框、section 和 pre，不需要 CSS。

# 8.4 数据库阶段前端函数——仍然是简单 DOM + fetch

数据库替换的是后端存储方式。对前端而言，已经稳定的 URL 和 JSON 应尽量保持不变。因此文章列表、详情、创建、编辑、事件列表和下注函数可以继续使用，不需要因为后端换成数据库而重写页面。

本阶段只为真正新增的数据库功能增加下面这些函数。

### 前端函数卡：`loadComments`

#### 用户动作

打开一篇文章详情，或点击“刷新评论”。

#### 输入

当前选中的 post ID。

#### 处理顺序

1. 如果还没有选中文章，显示“请先选择文章”并结束。
2. 把评论区域写成“正在加载评论……”。
3. 请求 `GET /api/v1/posts/{postId}/comments`。
4. 检查状态码。
5. 读取 JSON。
6. 清空旧评论区域。
7. items 为空时显示“暂无评论”。
8. 遍历 items，每条只创建一个 `<p>`，文字包含作者和内容。
9. 更新“共 N 条评论”。

#### 为什么评论列表不直接从文章详情对象中读取

评论数量可能很多，需要独立分页和刷新。把它们全部塞进文章详情会让详情响应不断变大。

---

### 前端函数卡：`submitComment`

#### 页面最小元素

- 一个评论输入框或 textarea；
- 一个提交按钮；
- 一个错误消息段落。

#### 处理顺序

1. 确认已选文章。
2. 读取评论文字并 trim。
3. 空文字不发送。
4. 禁用提交按钮。
5. 发送 `POST /api/v1/posts/{postId}/comments`，携带 Bearer token 和 JSON body。
6. 201 时清空输入框。
7. 调用 `loadComments()` 重新取得数据库真相。
8. 401 时提示登录。
9. 403/409 时显示后端 detail，例如“草稿不允许普通用户评论”。
10. finally 恢复按钮。

#### 为什么成功后重新加载，而不是只把请求内容 append 到页面

服务端返回的评论还包含数据库 ID、创建时间、清理后的文本和真实作者。重新读取或使用完整成功响应，比前端自己造一个对象可靠。

---

### 前端函数卡：`loadBalance`

#### 用户动作

登录完成、下注成功或点击“刷新余额”。

#### 处理顺序

1. 请求 `GET /api/v1/users/me/balance`。
2. 携带 token。
3. 401 时把余额区域显示为“请先登录”。
4. 成功时读取 `balance_points`。
5. 使用 `textContent` 显示整数积分。
6. 把返回值保存到当前前端变量，只用于显示和下注前提示。

#### 为什么不能把前端变量当余额真相

用户可以修改浏览器变量，多个标签页也可能同时下注。后端事务查询到的数据库余额才是真实判断依据。

---

### 前端函数卡：`loadMyBets`

#### 用户动作

点击“我的下注”。

#### 处理顺序

1. 请求 `GET /api/v1/users/me/bets`。
2. 清空旧记录容器。
3. items 为空时显示“暂无下注”。
4. 每笔创建一个 `<p>`，显示事件 ID、选项、积分和状态。
5. 不显示其他用户下注。
6. 如果接口支持分页，使用与阶段 3 完全相同的 skip/limit 规则。

#### 返回字段的页面用途

- bet_id：后续查回执或客服定位；
- event_id：点击后打开事件详情；
- option_id/label：显示选择；
- amount_points：显示投入；
- status：显示是否已结算/退款。

---

### 前端函数卡：`loadLedger`

#### 用户动作

点击“积分记录”。

#### 处理顺序

1. 请求 `GET /api/v1/users/me/ledger`。
2. 按后端返回顺序渲染。
3. `change_points` 为负数时显示“扣除 N”；为正时显示“增加 N”。
4. 显示 reason 和 created_at。
5. 页面最后显示后端返回的当前余额，若接口包含该字段。

#### 为什么账本和余额都要显示

余额只是当前结果；账本解释余额为什么变成这个结果。出现争议时可以逐笔核对。

---

### 前端函数卡：`handleDatabaseBet`

#### 与阶段 2 的 `handleBet` 最大区别

请求 URL 和主要 body 可以不变，但成功响应会增加新的真实字段，例如：

- bet_id；
- new_balance_points；
- option_pool_points；
- replayed。

#### 完整处理顺序

1. 读取事件、选项和整数积分。
2. 生成本次点击的 Idempotency-Key。
3. 禁用下注按钮。
4. 发送带 token 和幂等 Header 的 POST。
5. 成功时显示回执。
6. 使用 `new_balance_points` 立即更新余额文字。
7. 再调用 `loadBalance()` 和 `loadEventDetail()` 校准页面。
8. replayed=true 时显示“重复请求已复用，未再次扣款”。
9. 409 时显示余额不足、事件关闭或幂等冲突的具体 detail。
10. finally 恢复按钮，但事件不开放时保持禁用。

#### 为什么既使用返回的新余额，又重新 GET

成功响应能立即更新页面；重新 GET 是一次校准，确认页面与数据库最终状态一致。学习阶段多一次请求换来更容易理解的一致性。

---

### 前端函数卡：`handleSettleEvent`

#### 页面最小元素

- winning option 的 select；
- “确认结算”按钮；
- 一个 `<pre>` 显示结算摘要。

#### 处理顺序

1. 确认当前用户是管理员；前端检查只为体验，后端仍鉴权。
2. 读取 winning_option_id。
3. 在页面再次显示“将把哪一个选项设为获胜”，要求用户确认。
4. 发送管理员结算 POST。
5. 成功时显示：事件 ID、获胜选项、奖励用户数、总发放积分。
6. 重新加载事件详情。
7. 409 已结算时显示后端说明，不再次提交。
8. finally 恢复按钮；已结算事件保持禁用。


## 阶段 8 验收

- 重启后文章和事件仍存在。
- 密码哈希不出现在响应。
- 列表分页由数据库完成。
- 下注余额、Bet、账本和奖池同一事务提交。
- 余额不足时四项都不改变。
- 结算不能重复执行。
- 前端仍调用原有核心 API，没有重新改成静态数组。

---

# 阶段 9：把已经跑通的原生 DOM + fetch 迁移到 Vue 3


## 进入条件

完整阅读 Vue 3 Quick Start，并至少理解：

- 创建 Vue 应用；
- `ref`；
- 模板插值；
- `v-for`；
- `v-if`；
- `v-model`；
- `@click` 和 `@submit`；
- `onMounted`；
- 单文件组件。

## 为什么现在才学 Vue

你已经亲手完成：

- 状态变量；
- fetch；
- 手工创建按钮；
- 手工更新 textContent；
- 表单读取；
- 加载和错误状态。

Vue 现在解决的是你已经真实遇到的问题：状态改变后自动更新 DOM。

它不是替代后端，也不改变 HTTP API。

---

# 9.1 原生 JavaScript 到 Vue 的对应关系

| 原生做法 | Vue 做法 | 含义 |
|---|---|---|
| 普通变量 `posts` | `ref([])` | 需要被模板观察的状态 |
| 手工 createElement | `v-for` | 根据数组声明列表 |
| 手工 textContent | `{{ value }}` | 根据状态显示文字 |
| input.value | `v-model` | 表单值与状态连接 |
| addEventListener | `@click` / `@submit` | 声明事件函数 |
| 页面加载后调用函数 | `onMounted()` | 组件挂载后加载数据 |

## `ref` 为什么有 `.value`

在 JavaScript 逻辑中，Vue 需要一个可追踪包装对象。修改 `posts.value` 时，Vue 知道模板依赖发生变化并更新页面。

模板中通常不写 `.value`，Vue 会自动解包。

---

# 9.2 最小 Vue 项目结构

```text
frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── api.js
│   └── components/
│       ├── LoginForm.vue
│       └── MessageBox.vue
├── index.html
└── package.json
```

前期不要立刻拆十几个组件。

第一步可以把博客页面全部写在 `App.vue`，跑通后只拆最明显的登录表单和列表。

---

## 博客 Vue 状态
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts/{post_id}/navigation`
- **后端函数**：`build_post_navigation`


建议：

- `posts`：当前页文章摘要；
- `total`；
- `skip`；
- `limit`；
- `keyword`；
- `selectedPost`；
- `loading`；
- `message`；
- `accessToken`；
- 创建表单的 `title`、`content`。

### Vue 函数卡：`loadPosts`

#### 和原生版是否不同

HTTP 逻辑几乎一样。

不同的是：

- 不再清空 DOM 容器；
- 不再 createElement；
- 只把 `posts.value = data.items`；
- 模板中的 `v-for` 自动更新。

#### 处理步骤

1. `loading.value = true`；
2. 调用 API；
3. 保存 items 和 total；
4. 如果当前页为空且 skip > 0，可退回上一页再加载；
5. 捕获错误写入 message；
6. finally 把 loading 设为 false。

#### 为什么 finally 很重要

成功或失败都要结束加载状态，否则按钮可能一直禁用。

## Vue 模板中的文章按钮

概念：

```text
对 posts 中每个 post 创建一个按钮
按钮点击调用 selectPost(post.id)
```

必须使用稳定的 `post.id` 作为 key，不用数组下标。

### Vue 函数卡：`selectPost`

1. 请求详情；
2. 把结果保存到 `selectedPost.value`；
3. 模板使用 `v-if` 判断是否有选中文章；
4. 用插值和 `<pre>` 显示内容。

不要使用 `v-html` 显示未清洗 Markdown。

### Vue 函数卡：`submitPost`

1. 验证表单状态；
2. POST；
3. 成功清空字段；
4. 重新 loadPosts；
5. 选中新文章；
6. 显示成功消息。

#### `v-model` 做什么

输入框内容自动写入对应 ref；ref 改变也会反映到输入框。

但后端仍然必须验证。Vue 表单绑定不是安全措施。

---

### 接口卡：`GET /api/v1/posts/{post_id}/navigation`

**建议路由函数名：** `get_post_navigation`

**用户从页面上做什么：** 详情页点击“上一篇/下一篇”。

**这个功能为什么值得在本阶段加入：** 它是小而实用的页面辅助接口，练习相邻记录查找，不引入复杂推荐。

**输入来自哪里：** `post_id` path；可选 tag query。

**后端必须按下面顺序处理：**

1. 查当前已发布文章。
2. 按固定顺序取得同一筛选范围的文章摘要。
3. 找到当前文章位置。
4. 前一个作为 previous，后一个作为 next。
5. 首尾边界返回 null。

**成功时返回什么：** 200，返回 `previous` 和 `next` 摘要或 null。

**可能失败的情况：** 当前文章 404；query 422。

**前端怎样调用和更新页面：** Vue 详情组件在文章加载后请求；为 null 时禁用对应按钮。

**本功能重点函数或语法：** 列表索引、None→JSON null、响应模型。

**本阶段仍然没有解决什么：** 大数据量后可改成两条数据库查询。

### 后端函数卡：`build_post_navigation`

**函数类型：** 纯函数

**由谁调用：** navigation 路由

**接收什么：** 有序摘要列表、current_id。

**返回什么：** previous/next 对象。

**内部处理顺序：**

1. 遍历找到当前索引。
2. 索引大于 0 才取 previous。
3. 索引小于最后位置才取 next。
4. 返回对象。

**为什么要单独写这个函数：** 边界逻辑可单独测试。

**重点语法或方法：** `enumerate`、列表下标。

**边界与限制：** 不存在 current_id 应由调用者先处理。

### 前端函数说明卡：`loadPosts（Vue版本）`
- **所在页面**：App.vue或BlogHome.vue
- **什么时候执行**：onMounted和筛选提交
- **请求哪个后端功能**：client.listPosts
- **执行顺序**：
  1. 设置loadingPosts=true和清空旧错误。
  2. await API。
  3. 给posts.value赋返回items。
  4. 若当前选中ID已不在列表，清空selectedPost。
  5. finally关闭loading。
- **需要更新的页面区域**：PostList自动根据posts重新渲染。
- **这里首次出现的新 JavaScript API**：`onMounted`表示组件首次挂到页面后执行；本阶段只用它加载初始数据。

### 前端函数说明卡：`selectPost（Vue版本）`
- **所在页面**：App.vue或BlogHome.vue
- **什么时候执行**：PostList发出select事件
- **请求哪个后端功能**：client.getPost
- **执行顺序**：
  1. 设置loadingDetail。
  2. 请求详情。
  3. 给selectedPost.value赋值。
  4. 失败时清空旧详情。
- **需要更新的页面区域**：PostDetail自动更新。
- **这里首次出现的新 JavaScript API**：Props向下传值，组件事件向上通知；不需要复杂状态库。

### 前端函数说明卡：`submitPost（Vue版本）`
- **所在页面**：App.vue/编辑页面
- **什么时候执行**：PostEditor提交
- **请求哪个后端功能**：client.createPost
- **执行顺序**：
  1. 接收表单普通对象。
  2. 附token请求。
  3. 成功后把新摘要插入posts或重新loadPosts。
  4. 选择新文章。
- **需要更新的页面区域**：列表和详情。

## 预测市场 Vue 状态
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/users/me/dashboard`
- **后端函数**：`build_user_dashboard`


- `events`；
- `selectedEvent`；
- `statusFilter`；
- `keyword`；
- `betAmount`；
- `balance`；
- `currentUser`；
- `message`；
- `loading`；
- `submittingBet`。

### Vue 函数卡：`loadEvents`

#### 与原生 JavaScript 版本相比，什么没有变化

请求 URL、查询参数、后端 JSON 和错误规则都不变。变化的只是页面更新方式：原生版本手工创建按钮，Vue 版本只修改响应式变量。

#### 输入状态

- `keyword.value`：当前搜索词；
- `statusFilter.value`：当前状态筛选；
- `skip.value`：跳过条数；
- `limit.value`：每页上限。

#### 完整处理步骤

1. 把 `loading.value` 设为 `true`。
2. 清空旧错误消息，但不要提前清空旧列表，以免页面闪成空白。
3. 用 `URLSearchParams` 放入 keyword、status、skip、limit。
4. 调用公共请求函数，请求事件列表。
5. 成功后把 `data.items` 赋给 `events.value`。
6. 把 `data.total` 赋给 `total.value`。
7. 根据 total 与当前 items 数量计算上一页、下一页按钮是否可用。
8. 失败时把错误文字放入 `message.value`，保留或清空旧数据的策略要统一。学习项目建议保留旧数据并明确提示“刷新失败”。
9. 在 `finally` 中把 `loading.value` 设回 `false`。

#### 模板如何得到按钮

模板使用 `v-for="event in events"`。当 `events.value` 被替换时，Vue 自动更新按钮，不需要 `createElement`、`append` 或手工清空容器。

### Vue 函数卡：`selectEvent`

请求详情并保存 `selectedEvent`。

模板通过 `v-for` 显示 options。

### Vue 函数卡：`placeBet`

#### 输入

`optionId` 来自模板按钮；积分来自 `betAmount`。

#### 处理步骤

1. 检查用户已登录；
2. 把输入转换为数字；
3. 检查正整数；
4. 防止重复提交；
5. POST；
6. 保存返回的新余额；
7. 重新加载事件详情；
8. 显示下注 ID；
9. finally 恢复提交状态。

#### 为什么不直接对本地 pool 加积分

服务器可能拒绝请求，或同时有其他用户下注。重新读取后端结果更可靠。

---

### 接口卡：`GET /api/v1/users/me/dashboard`

**建议路由函数名：** `get_my_dashboard`

**用户从页面上做什么：** Vue 个人首页加载。

**这个功能为什么值得在本阶段加入：** 余额、最近下注、未结算持仓数量分散在多个接口；有限摘要可以减少页面初始化的请求数量。

**输入来自哪里：** Bearer token；`recent_limit` query。

**后端必须按下面顺序处理：**

1. 取得当前用户。
2. 查询余额。
3. 查询最近 N 条下注摘要。
4. 统计未结算持仓与待退款数量。
5. 组装小型响应，不返回全部历史。

**成功时返回什么：** 200，返回 balance、recent_bets、open_position_count、pending_refund_count。

**可能失败的情况：** 401、limit 422。

**前端怎样调用和更新页面：** Vue `onMounted` 调用一次；模板只显示少量文字和最近记录。

**本功能重点函数或语法：** 有限聚合响应；避免 N+1。

**本阶段仍然没有解决什么：** 详细列表仍使用原端点。

### 后端函数卡：`build_user_dashboard`

**函数类型：** service 查询函数

**由谁调用：** dashboard 路由

**接收什么：** Session、user_id、recent_limit。

**返回什么：** DashboardResponse。

**内部处理顺序：**

1. 执行有限数量查询。
2. 转换公开字段。
3. 组装并返回。

**为什么要单独写这个函数：** 路由不应塞入多个查询和拼装细节。

**重点语法或方法：** SQLModel select、limit。

**边界与限制：** 不返回其他用户数据。

### 前端函数说明卡：`loadEvents（Vue版本）`
- **所在页面**：App.vue/MarketHome.vue
- **什么时候执行**：onMounted或筛选提交
- **请求哪个后端功能**：client.listEvents
- **执行顺序**：
  1. 设置loading。
  2. 请求列表。
  3. 更新events。
  4. 若没有选中事件且列表非空，调用selectEvent第一项。
- **需要更新的页面区域**：EventList和空状态。

### 前端函数说明卡：`placeBet（Vue版本）`
- **所在页面**：MarketHome.vue
- **什么时候执行**：BetForm发出submit
- **请求哪个后端功能**：client.placeBet
- **执行顺序**：
  1. 检查前端输入为正整数。
  2. 生成幂等键。
  3. 设置placingBet=true。
  4. 发送请求。
  5. 成功后并行或依次重新加载事件详情、余额和我的下注。
  6. finally恢复按钮。
- **需要更新的页面区域**：BetForm结果、EventDetail池子、AccountPanel余额。
- **这里首次出现的新 JavaScript API**：`computed` 用于从 `selectedEvent` 计算总池或是否可下注；不要用 `watch` 复制同一份数据。

# 9.3 组件拆分原则

## 什么时候拆组件

一个区域满足至少一项时考虑拆：

- 有独立输入和事件；
- 在多个页面复用；
- 逻辑明显独立；
- App.vue 已经很难阅读。

## 初期推荐组件

博客：

- `LoginForm`；
- `PostList`；
- `PostEditor`。

预测市场：

- `LoginForm`；
- `EventList`；
- `BetForm`；
- `BalancePanel`。

## Props 与事件的简单规则

- 父组件把数据通过 props 传给子组件；
- 子组件通过 emit 告诉父组件发生了动作；
- 子组件不要偷偷修改父组件的复杂对象。

不需要现在引入 Pinia。


## 阶段 9 验收

- Vue 页面仍请求真实 FastAPI。
- 没有复制 mock 数据替代 API。
- `v-for` 使用业务 ID。
- 表单使用 `v-model`。
- API 错误显示在页面。
- 组件数量保持少而清楚。
- 不使用未清洗 `v-html`。

---

# 阶段 10：JSON Lines、SSE、后台任务与静态文件——只做最小实用功能


## 进入条件

读完：

- 流式传输 JSON Lines；
- 服务器发送事件 SSE；
- 后台任务；
- 元数据和文档 URL；
- 前端；
- 静态文件；
- Advanced 流式数据。

## 为什么把它们放在数据库之后

流式导出和实时通知必须有稳定数据来源。否则只是在内存数组上演示语法，项目价值很低。

本阶段不要同时做复杂消息队列、任务平台和断点续传。

---

## 个人博客系统：JSONL 导出
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts/export.jsonl`、`GET /api/v1/posts/events`、`POST /api/v1/posts/{post_id}/publish（后台任务升级）`
- **后端函数**：`write_publish_audit`


### 接口卡：`GET /api/v1/posts/export.jsonl`

#### 建议路由函数名

`export_posts_jsonl`

#### JSON Lines 是什么

普通 JSON 数组：

```text
[{...}, {...}, {...}]
```

JSONL 是每行一个独立 JSON 对象：

```text
{"id":1,"title":"A"}
{"id":2,"title":"B"}
{"id":3,"title":"C"}
```

#### 为什么有用

- 可以逐行产生；
- 数据大时不必先构造完整大数组；
- 日志和数据导出工具容易逐行处理。

#### 处理步骤

1. 验证管理员权限或公开导出规则；
2. 查询文章；
3. 一次取一条或分批取；
4. 转成公开导出字段；
5. JSON 编码；
6. 末尾加换行；
7. 逐行发送。

#### 导出字段

只包括需要的公开字段，不导出密码、内部备注或 token。

#### 前端交互

最简单方式是提供一个普通下载链接或按钮跳转到导出 URL。

不需要用 fetch 把整个文件读进内存再创建下载。

---

## 个人博客系统：SSE 发布事件

### 接口卡：`GET /api/v1/posts/events`

#### 建议路由函数名

`stream_post_events`

#### SSE 是什么

浏览器建立一个长期 HTTP 连接。服务器可以不断向浏览器发送文本事件。

它是单向的：服务器 → 浏览器。

#### 适合什么

- 新文章发布通知；
- 导入进度；
- 后台处理状态。

#### 不适合什么

需要浏览器持续向服务器发实时消息时，应考虑 WebSocket。

#### 事件示例

```text
event: post_published
data: {"post_id": 10, "title": "新文章"}
```

#### 后端处理步骤

1. 建立事件生成器；
2. 等待事件来源；
3. 产生符合 SSE 格式的文本；
4. 定期发送心跳，避免某些代理关闭空闲连接；
5. 客户端断开时结束生成器并清理资源。

学习版可以使用内存队列，但必须标注单进程限制。

### 前端函数卡：`connectPostEvents`

#### 新浏览器 API：`EventSource`

它专门连接 SSE URL，不需要你手写持续 fetch 循环。

#### 处理步骤

1. 创建 EventSource；
2. 监听 `post_published`；
3. 收到后解析 `event.data`；
4. 显示通知；
5. 调用 `loadPosts()`；
6. 监听错误；
7. 组件卸载时 close。

#### 身份限制

EventSource 原生 API 不方便添加 Authorization 请求头。

初学阶段 SSE 可以只传公开发布事件。需要受保护 SSE 时再研究 Cookie、短期签名 URL 或 fetch stream，不在核心主线硬塞。

---

## 后台任务卡：`write_publish_audit`

### 补充拆解

- **函数类型**：后台任务函数
- **由谁调用**：publish_post成功后
- **接收什么**：post_id、actor_id、request_id。
- **返回什么**：无HTTP返回值。
- **内部顺序**：
  1. 写一条简短审计记录。
  2. 捕获并记录自身错误。
- **注意事项**：不能接收Request对象或Session后在响应后继续使用已经关闭的请求资源；只传简单数据。


### 功能

文章发布成功响应返回后，写一条非关键审计文本或发送学习通知。

### 为什么可以后台执行

它不是决定文章是否发布的核心步骤。即使通知稍后完成，文章发布结果仍有效。

### 不能放后台的操作

- 扣余额；
- 创建下注；
- 结算；
- 必须与请求事务一致的核心数据。

### 处理步骤

1. 发布事务先成功；
2. 把审计任务加入 BackgroundTasks；
3. 返回响应；
4. FastAPI 在响应后执行轻量任务。

任务很重或必须可靠重试时，应使用外部任务队列，不使用进程内 BackgroundTasks 冒充生产队列。

---

### 接口说明卡：`POST /api/v1/posts/{post_id}/publish（后台任务升级）`
- **建议路由函数名**：`publish_post`。
- **这个后端功能可以做什么**：发布成功后追加非关键工作，例如写审计文本或模拟发送通知。
- **输入从哪里来**：与阶段6相同。
- **路由函数的核心职责**：核心发布事务在响应前完成；BackgroundTasks只接收非关键附带函数。
- **处理顺序**：
  1. 完成权限、状态、数据库发布并commit。
  2. 生成post.published领域事件。
  3. 把轻量审计/模拟通知加入BackgroundTasks。
  4. 返回成功。
- **成功返回**：200，PostDetail。
- **失败返回**：核心发布失败按原错误；后台任务失败只记录日志，不能把已经返回成功的发布变成未发布。
- **前端拿到结果后做什么**：发布后页面等待SSE刷新或直接更新。
- **本阶段仍然存在的限制**：搜索索引若是关键能力不能只依赖BackgroundTasks。

## 事件竞猜与预测市场：事件 SSE
### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/events/{event_id}/stream`、`GET /api/v1/events/export.jsonl`
- **后端函数**：`send_bet_confirmation`


### 接口卡：`GET /api/v1/events/{event_id}/stream`

#### 功能

推送：

- 奖池变化摘要；
- 事件关闭；
- 事件结算。

#### 事件数据示例

```json
{
  "type": "pool_updated",
  "event_id": 4,
  "options": [
    {"id": 9, "pool_points": 240},
    {"id": 10, "pool_points": 190}
  ]
}
```

#### 为什么推送数据库提交后的状态

如果事务还没有 commit 就广播，之后事务失败，前端会看到一个从未真正存在的状态。

正确顺序：

1. 事务成功提交；
2. 再发布通知。

#### 学习版限制

内存事件队列在多 worker 下不共享。先完成单进程理解，生产阶段说明外部消息系统。

### 前端函数卡：`connectEventStream`

1. 当前选中事件变化时，关闭旧 EventSource；
2. 为新事件创建连接；
3. 收到 pool_updated 时，最简单可靠的做法是调用 `selectEvent(eventId)` 重新请求完整详情；
4. 收到 settled 时刷新详情并禁用下注；
5. 组件卸载时关闭。

#### 为什么不直接手工合并每个推送字段

初学阶段完整刷新更容易保证一致。等性能确实成为问题，再局部更新。

---

## 静态文件

如果选择由 FastAPI 同时提供构建后的 Vue 文件，可以挂载静态目录。

但开发阶段仍建议：

- Vue 开发服务器运行前端；
- FastAPI 运行 API；
- CORS 连接。

生产部署再决定是否同一服务提供。


### 接口说明卡：`GET /api/v1/events/export.jsonl`
- **建议路由函数名**：`export_events_jsonl`。
- **这个后端功能可以做什么**：导出公开事件及最终结果。
- **输入从哪里来**：状态/时间筛选；只含公开字段。
- **路由函数的核心职责**：分批查询并逐行输出。
- **处理顺序**：
  1. 验证筛选。
  2. 查询公开事件。
  3. 逐条输出event summary/result。
- **成功返回**：200流式JSONL。
- **失败返回**：422；发送前数据库错误500。
- **前端拿到结果后做什么**：提供下载按钮。
- **本阶段仍然存在的限制**：不导出用户私有下注。

### 后端函数说明卡：`send_bet_confirmation`
- **函数类型**：后台任务函数
- **由谁调用**：下注事务成功后
- **接收什么**：user_id、bet_id和简单通知内容。
- **返回什么**：无。
- **内部顺序**：
  1. 模拟写通知日志。
- **注意事项**：扣款、bet和ledger已经在事务内完成；通知失败不回滚下注。

## 阶段 10 验收

- JSONL 每行都是独立合法 JSON。
- 导出不包含敏感字段。
- SSE 连接能关闭并清理。
- 前端离开页面不会留下永久 EventSource。
- 后台任务不承担余额和结算核心事务。
- 推送只发生在数据库提交成功后。

---

# 阶段 11：测试、调试与回归安全网


## 进入条件

完成 FastAPI Tutorial 的“测试、调试”，并阅读 Advanced 中与你当前项目有关的：

- 测试 lifespan；
- 覆盖依赖项；
- 异步测试。

WebSocket 测试暂时留到阶段 14。

## 本阶段为什么仍然是“前后端并行”

这一阶段不是暂停开发去“补测试理论”。后端要把已经能运行的接口固定成自动化测试；前端要把每一个主要页面动作整理成一份真实联调清单，并确认 loading、成功、空数据和错误四种状态都能看见。

你不会用静态数组代替接口。测试使用的是**独立测试数据库**，前端手工验收使用的仍然是真实 FastAPI 服务。

## 两个项目共用的测试基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`create_test_app`、`create_test_user`、`login_and_get_headers`、`test_empty_patch_changes_nothing`、`test_client fixture`、`build_auth_headers`

## 11.1 先理解一条后端测试到底在做什么

一条 API 测试通常包含四段：

1. **准备（Arrange）**：准备用户、文章、事件、余额或登录身份。
2. **执行（Act）**：像浏览器一样发送一次真实 HTTP 请求。
3. **检查响应（Assert Response）**：检查状态码和 JSON 字段。
4. **检查数据不变量（Assert State）**：重新查询数据库，确认该改的真的改了，不该改的没有被误改。

只检查 `status_code == 200` 远远不够。例如下注接口即使错误地扣了两次余额，也可能仍然返回 201。真正重要的是检查余额、下注、账本和奖池是否同时保持一致。

---

### 共用测试函数卡：`create_test_app`

#### 函数类型

测试应用工厂。

#### 为什么需要它

开发应用通常读取开发数据库地址、真实密钥和本地上传目录。测试不能直接复用这些外部状态，否则一次错误测试可能删掉你的开发文章或修改真实余额。

#### 接收什么

- 测试数据库地址；
- 测试配置；
- 可选的临时上传目录。

#### 返回什么

一个只供本轮测试使用的 FastAPI 应用对象。

#### 完整处理顺序

1. 创建测试配置，明确环境名为 `test`。
2. 数据库地址指向临时 SQLite 文件或独立测试数据库。
3. JWT 密钥使用测试专用字符串，不读取生产密钥。
4. 上传目录指向 pytest 提供的临时目录。
5. 创建应用并注册与正式应用相同的路由。
6. 返回应用对象。

#### 为什么不在测试里直接修改全局 `app`

如果所有测试共用一个已经加载过的全局应用，依赖覆盖、中间件和配置可能在测试之间残留。应用工厂能让测试边界更清楚，也让后面的部署配置更容易。

---

## 共用测试 fixture 卡：`client`

### 函数类型

pytest fixture。

### 由谁使用

所有同步 HTTP API 测试。

### 返回什么

一个 `TestClient`。

### 完整处理顺序

1. 调用 `create_test_app` 得到测试应用。
2. 创建测试数据库表。
3. 覆盖 `get_session`，让路由取得测试 Session。
4. 使用 `with TestClient(app)` 进入上下文。
5. 进入上下文时触发应用 lifespan 的启动部分。
6. `yield client`，让测试发送请求。
7. 测试结束后退出上下文，触发 lifespan 清理。
8. 清空 `dependency_overrides`。
9. 删除临时数据库和临时上传文件。

### 最容易犯的错误

- 测试连接到了开发数据库；
- 测试结束后没有清除依赖覆盖；
- fixture 作用域设得过大，导致不同测试共享上一条测试的数据；
- 没有使用 `with TestClient(...)`，因此 lifespan 没有执行。

---

### 共用测试辅助函数卡：`create_test_user`

#### 函数类型

数据库准备辅助函数。

#### 接收什么

- Session；
- username；
- role；
- 初始积分；
- 是否启用。

#### 返回什么

已经写入测试数据库的用户对象。

#### 完整处理顺序

1. 检查测试参数是否合理，例如初始积分不能为负。
2. 使用与正式系统相同的密码哈希函数生成测试密码哈希。
3. 创建用户对象。
4. 写入并提交。
5. 刷新对象，确保取得数据库生成的 ID。
6. 返回用户。

#### 为什么不直接在每条测试里复制创建用户的步骤

认证测试很多。统一辅助函数能减少重复，同时保证所有测试用户都符合数据库约束。它仍然只是测试准备，不应该绕过被测试的核心业务。

---

### 共用测试辅助函数卡：`login_and_get_headers`

#### 函数类型

测试 HTTP 辅助函数。

#### 接收什么

- TestClient；
- username；
- password。

#### 返回什么

形如 `Authorization: Bearer ...` 的请求头字典。

#### 完整处理顺序

1. 调用真实的 `POST /api/v1/auth/token`。
2. 断言登录返回 200。
3. 读取 `access_token`。
4. 检查 token 字段不是空字符串。
5. 拼成 Bearer Header。
6. 返回 Header 字典。

#### 为什么多数业务测试应通过真实登录端点取得 token

这样可以同时验证表单编码、密码检查、token 签发和 Bearer 解析的整体链路。只有当某条测试专门关注非常下游的业务且登录步骤会制造大量噪声时，才考虑覆盖 `get_current_user`。

---

### 后端函数说明卡：`test_client fixture`
- **函数类型**：pytest fixture
- **由谁调用**：所有API测试
- **接收什么**：测试app和测试数据库。
- **返回什么**：TestClient。
- **内部顺序**：
  1. 创建独立测试数据库。
  2. 覆盖get_session依赖。
  3. 用with TestClient(app)触发lifespan。
  4. yield client。
  5. 结束后清理dependency_overrides和数据库。
- **注意事项**：绝不能连接开发数据库；每个测试之间不依赖顺序。

### 后端函数说明卡：`build_auth_headers`
- **函数类型**：测试辅助函数
- **由谁调用**：需要登录的测试
- **接收什么**：测试用户角色。
- **返回什么**：Authorization Header字典。
- **内部顺序**：
  1. 创建或取得测试用户。
  2. 调用登录端点或直接生成测试token。
  3. 返回Bearer Header。
- **注意事项**：关键登录流程本身仍要通过真实端点测试；其他业务测试可用依赖覆盖减少重复。

## 个人博客系统：测试任务
### 本项目本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`test_list_posts_returns_summaries_only`、`test_post_pagination_uses_filtered_total`、`test_get_missing_post_returns_404`、`test_create_post_uses_current_user_as_author`、`test_other_author_cannot_update_post`、`test_markdown_too_large_leaves_no_partial_file`、`test_comment_on_unpublished_post_is_rejected`、`seed_users_and_posts`、`test_create_post_then_fetch`、`test_upload_too_large_creates_nothing`


### 测试函数卡：`test_list_posts_returns_summaries_only`

#### 要证明什么

文章列表只返回摘要，不泄露正文和内部字段。

#### 准备

创建两篇已发布文章，其中内部对象含有：

- `content`；
- `internal_note`；
- `deleted`。

#### 执行

请求：

```text
GET /api/v1/posts?skip=0&limit=5
```

#### 检查响应

1. 状态码为 200。
2. 有 `items`、`total`、`skip`、`limit`。
3. `total` 等于符合条件的文章总数。
4. 每个 item 有 `id`、`title`、`author`。
5. 每个 item 都没有 `content`、`internal_note`、`deleted`。

#### 为什么这条测试很重要

响应模型配置如果被误删，内部字段可能悄悄出现在接口中。页面看起来仍能工作，但数据安全已经退化。这条测试能立即发现这种回归。

---

### 测试函数卡：`test_post_pagination_uses_filtered_total`

#### 要证明什么

`total` 是“所有符合搜索条件的数量”，不是当前页的长度。

#### 准备示例

创建 7 篇文章，其中 5 篇标题包含 `fastapi`。

#### 执行

```text
GET /api/v1/posts?keyword=fastapi&skip=0&limit=2
```

#### 预期

- `items` 长度为 2；
- `total` 为 5；
- `skip` 为 0；
- `limit` 为 2。

#### 第二次请求

```text
GET /api/v1/posts?keyword=fastapi&skip=4&limit=2
```

预期只返回 1 条，但 `total` 仍然是 5。

#### 这和前端有什么关系

前端使用 `skip + items.length < total` 判断下一页按钮是否可用。如果后端错误地把 `total` 写成当前页长度，前端会过早禁用下一页。

---

### 测试函数卡：`test_get_missing_post_returns_404`

#### 执行

请求一个数据库中不存在的 ID。

#### 检查

- 状态码为 404；
- JSON 中 `code` 为 `POST_NOT_FOUND`；
- `detail` 是可显示给用户的说明；
- 不返回 Python traceback。

#### 额外检查

确认数据库没有因为一次只读请求发生任何变化。

---

### 测试函数卡：`test_create_post_uses_current_user_as_author`

#### 要证明什么

作者身份来自登录用户，而不是浏览器随意提交的 `author` 字段。

#### 准备

创建并登录 author 用户。

#### 执行

发送创建请求，只提交标题、正文和标签。

#### 检查

- 状态码 201；
- 返回文章的 `author.id` 是当前用户 ID；
- 数据库文章的 `author_id` 也是当前用户 ID；
- 请求中即使恶意增加另一个 `author_id`，也会被模型拒绝或忽略，不能冒充他人。

---

### 测试函数卡：`test_other_author_cannot_update_post`

#### 准备

1. 用户 A 创建文章。
2. 用户 B 登录。

#### 执行

用户 B 请求：

```text
PATCH /api/v1/posts/{A的文章ID}
```

#### 检查

- 返回 403；
- 错误 code 明确；
- 重新查询数据库，标题和正文仍是原值；
- `updated_at` 也不应被误更新。

#### 为什么必须检查数据库

如果权限检查错误地放在字段修改之后，路由可能先改对象再抛 403。仅检查状态码发现不了这种副作用。

---

### 测试函数卡：`test_markdown_too_large_leaves_no_partial_file`

#### 准备

生成超过上传上限的 Markdown 字节内容，使用 pytest 临时目录作为存储目录。

#### 执行

向导入接口发送 multipart 请求。

#### 检查

- 状态码 413；
- 错误 code 为文件过大；
- 数据库中没有创建文章；
- 临时目录中没有半截目标文件；
- 如果实现使用临时文件，临时文件也已被清理。

#### 这条测试保护什么

上传失败不能留下“数据库没有文章但磁盘有垃圾文件”或“数据库有文章但文件只有一半”的不一致状态。

---

### 测试函数卡：`test_empty_patch_changes_nothing`

#### 执行

对已有文章发送空 JSON 对象。

#### 检查

按照手册约定返回 400；数据库所有可编辑字段和 `updated_at` 都保持不变。

#### 为什么需要它

如果空 PATCH 被当成成功，前端可能显示“保存成功”，但用户实际上没有修改任何内容。明确拒绝更容易排查表单逻辑。

---

### 测试函数卡：`test_comment_on_unpublished_post_is_rejected`

#### 准备

创建草稿文章和普通 reader 用户。

#### 执行

reader 调用评论创建接口。

#### 检查

- 返回 403 或按你固定契约使用 409；全项目只能选一种；
- 评论表没有新增记录；
- 文章评论数量没有变化。

---

### 后端函数卡：`seed_users_and_posts`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 创建用户与哈希密码。
2. 创建不同状态文章。
3. commit。
4. 返回对象。

**为什么要单独写这个函数：** 统一创建测试用户、草稿和发布文章。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

### 后端函数卡：`test_create_post_then_fetch`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. POST 创建并断言 201。
2. GET 详情断言正文。
3. GET 列表断言不含正文。

**为什么要单独写这个函数：** 创建后列表与详情契约一致。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

### 后端函数卡：`test_upload_too_large_creates_nothing`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 记录文章数。
2. 上传超限文件。
3. 断言 413。
4. 重新查询数量不变。

**为什么要单独写这个函数：** 超限文件不能留下数据。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

## 事件竞猜与预测市场：测试任务
### 本项目本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`test_place_bet_updates_all_four_records`、`test_same_idempotency_key_does_not_charge_twice`、`test_same_key_with_different_body_returns_409`、`test_insufficient_balance_rolls_back_everything`、`test_expired_event_rejects_bet_with_fixed_clock`、`test_settlement_is_idempotent`、`test_refund_creates_exactly_one_credit_per_bet`、`fixed_clock_override`、`test_idempotent_bet_replay`、`test_insufficient_balance_is_atomic`、`test_refund_is_idempotent`


### 测试函数卡：`test_place_bet_updates_all_four_records`

#### 要证明什么

一次成功下注必须同时正确改变：

1. 用户余额；
2. Bet 下注记录；
3. Ledger 账本记录；
4. OptionPool 选项奖池。

#### 准备示例

- 用户余额：1000；
- 选项池：300；
- 下注：200。

#### 执行

发送真实下注请求。

#### 预期数据库状态

- 用户余额变为 800；
- 新增一条 bet，金额 200；
- 新增一条 ledger，变化量 -200，业务引用指向 bet；
- 选项池变为 500。

#### 响应检查

- 首次成功 201；
- 回执中的余额、下注 ID 和选项池值与数据库一致。

---

### 测试函数卡：`test_same_idempotency_key_does_not_charge_twice`

#### 准备

使用完全相同的用户、event、option、amount 和 `Idempotency-Key`。

#### 执行

连续发送两次请求。

#### 检查

第一次：

- 201；
- `replayed=false`。

第二次：

- 200；
- `replayed=true`；
- 返回同一个 bet_id。

数据库：

- 只有一条 bet；
- 只有一条扣款 ledger；
- 余额只减少一次；
- 奖池只增加一次。

#### 为什么不能只检查第二次返回 200

错误实现可能第二次又扣款，然后仍返回第一次回执。数据库断言才能识别这种严重问题。

---

### 测试函数卡：`test_same_key_with_different_body_returns_409`

#### 执行顺序

1. 用 key=`abc` 下注 100。
2. 再用 key=`abc` 下注 200。

#### 检查

- 第二次返回 409；
- code 为 `IDEMPOTENCY_KEY_REUSED`；
- 余额、账本、下注和池子都没有第二次变化。

---

### 测试函数卡：`test_insufficient_balance_rolls_back_everything`

#### 准备

用户余额 50，尝试下注 100。

#### 检查

- 返回 409；
- 余额仍是 50；
- 没有 bet；
- 没有 ledger；
- 奖池没有变化；
- Session 在回滚后仍然可以执行下一条查询。

#### 这条测试为什么比“余额不能为负”更完整

最终余额没有变负，并不代表没有留下孤立 bet 或错误账本。必须检查整个事务内的所有对象。

---

### 测试函数卡：`test_expired_event_rejects_bet_with_fixed_clock`

#### 为什么使用固定时钟依赖

如果测试直接依赖真实当前时间，某些测试会在边界秒数偶尔失败。覆盖 `get_clock` 后，每次测试都可以明确说“现在是 12:00，deadline 是 11:59”。

#### 检查

- 截止前一秒可按规则下注；
- 截止时刻及之后返回 409；
- 失败时余额和池子不变。

---

### 测试函数卡：`test_settlement_is_idempotent`

#### 补充拆解

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 第一次结算。
2. 记录账本。
3. 第二次结算。
4. 断言无新增派奖。

**为什么要单独写这个函数：** 重复结算不重复派奖。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。


#### 准备

一个 closed 事件，两边都有下注。

#### 第一次结算

- 管理员提交 winning_option_id；
- 返回成功；
- 每个中奖用户只获得一次奖励账本；
- 事件变为 settled。

#### 第二次结算

按手册选择一种稳定行为：

- 返回 409，说明已结算；或者
- 返回原结算摘要并标记 replayed。

无论选择哪种，数据库都不能新增第二轮奖励。

---

### 测试函数卡：`test_refund_creates_exactly_one_credit_per_bet`

#### 准备

取消一个已有三笔下注的事件。

#### 执行

管理员调用退款接口两次。

#### 检查

- 每笔 bet 只对应一条退款 ledger；
- 用户余额只恢复一次；
- 第二次调用不会重复加积分；
- 退款状态明确为 completed。

---

### 后端函数卡：`fixed_clock_override`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 定义返回固定 UTC 时间的函数。
2. 写入 dependency_overrides。
3. 测试后清除。

**为什么要单独写这个函数：** 用固定时间测试截止规则。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

### 后端函数卡：`test_idempotent_bet_replay`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 记录余额与池。
2. 第一次下注。
3. 相同请求重放。
4. 断言只变化一次。

**为什么要单独写这个函数：** 同 key 重试只扣一次。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

### 后端函数卡：`test_insufficient_balance_is_atomic`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 记录 Bet/Ledger/Balance/Pool。
2. 提交超额下注。
3. 断言错误。
4. 逐项重查不变。

**为什么要单独写这个函数：** 余额不足时所有表不变。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

### 后端函数卡：`test_refund_is_idempotent`

**函数类型：** pytest fixture/测试函数

**由谁调用：** pytest

**接收什么：** 对应测试 fixture 和数据。

**返回什么：** 通过断言判断。

**内部处理顺序：**

1. 第一次退款。
2. 第二次退款。
3. 断言余额和账本只变化一次。

**为什么要单独写这个函数：** 重复退款不重复返钱。

**重点语法或方法：** TestClient、Session 重查、assert、dependency_overrides。

**边界与限制：** 不能只断言状态码，还要断言数据库状态。

# 11.4 前端并行验收函数

前端此时仍使用真实 API。你暂时不需要学习复杂前端测试框架，但应在 `scripts/manual-checks.js` 或学习日志中写清以下函数式检查。

### 前端函数卡：`runBlogSmokeCheck`

#### 作用

快速确认博客最重要的真实链路没有断。

#### 处理顺序

1. 调用健康检查。
2. 登录测试 author。
3. 创建一篇带随机标题的文章。
4. 用返回 ID 请求详情。
5. 修改标题。
6. 再次请求详情，确认页面显示新标题。
7. 删除文章。
8. 再请求详情，确认页面显示 404 错误。

#### 为什么不要把它做成隐藏 mock

它必须真正调用当前后端，目的就是发现 API base URL、CORS、认证头、请求体和响应解析之间的集成问题。

---

### 前端函数卡：`runPredictionSmokeCheck`

#### 处理顺序

1. 登录测试用户。
2. 加载当前余额。
3. 加载开放事件详情。
4. 下注最小积分。
5. 重新加载余额和事件。
6. 页面确认余额减少、奖池增加。
7. 使用同一幂等键重试，确认页面显示“重复请求已复用”，数值不再变化。

#### 注意

这类 smoke 函数只在本地测试账户使用。不要把管理员密钥、固定测试密码或自动下注按钮放进生产构建。


## 阶段 11 验收

- 测试数据库与开发数据库完全分开。
- 每条关键写操作至少有一个成功测试和一个失败不修改数据的测试。
- 分页测试明确检查 `total` 与当前页长度的区别。
- 幂等测试检查数据库次数，不只看响应文字。
- 前端 smoke check 调用真实后端，没有静态数组。
- 修复 bug 时先加入能复现 bug 的测试，再修改代码。

---

# 阶段 12：高级响应、下载、响应 Cookie/Header 与 OAuth2 Scopes


## 进入条件

阅读 Advanced 中的：

- 额外状态码；
- 直接返回 Response；
- 自定义响应；
- OpenAPI 附加响应；
- 响应 Cookie；
- 响应 Header；
- 更改响应状态码；
- 高级依赖；
- OAuth2 scopes；
- HTTP Basic；
- 直接使用 Request；
- dataclass。

## 本阶段的“不要炫技”原则

普通业务 JSON 仍然返回 Pydantic 响应模型。只有下面这些真实需求才直接控制 Response：

- 下载文件；
- CSV；
- 流式内容；
- 设置 Cookie；
- 增加必要响应 Header。

不要把所有路由都改成 `JSONResponse`。那会失去自动验证和清晰契约。

---

## 个人博客系统

### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/posts/{post_id}/download`、`POST /api/v1/preferences/page-size`、`POST /api/v1/posts/{post_id}/reading-events（响应Header实验）`
- **后端函数**：本阶段没有新增独立后端函数。

### 博客接口卡：`GET /api/v1/posts/{post_id}/download`

#### 补充拆解

- **建议路由函数名**：`download_post_markdown`。
- **这个后端功能可以做什么**：把文章以.md文件下载，而不是JSON显示。
- **输入从哪里来**：post_id；可选current_user用于草稿权限。
- **路由函数的核心职责**：先完成所有验证，再返回FileResponse或动态文本Response。
- **处理顺序**：
  1. 查文章和访问权限。
  2. 生成安全文件名，不使用含换行的用户输入。
  3. 准备UTF-8 Markdown内容。
  4. 设置正确media type和Content-Disposition。
  5. 返回响应。
- **成功返回**：200文件响应，浏览器触发下载。
- **失败返回**：401/403/404；发送前500。
- **前端拿到结果后做什么**：文章详情“下载Markdown”按钮直接导航到URL或fetch后创建下载。
- **本阶段仍然存在的限制**：直接Response绕过部分自动response_model，必须自己保证内容安全。


#### 建议路由函数名

`download_post_markdown`

#### 用户动作

文章详情页点击“下载 Markdown”。

#### 输入

- 路径参数 `post_id`；
- 当前用户，可选：公开文章无需登录，草稿需要作者或管理员。

#### 路由函数的核心职责

取得文章正文，构造一个安全的 `.md` 下载响应。

#### 完整处理顺序

1. 调用 `get_post_or_404`。
2. 检查文章是否公开；草稿时检查当前用户权限。
3. 取得文章标题，但**不能直接把任意标题原样放入响应头**。
4. 生成安全文件名，例如只保留常见字母、数字、短横线，无法转换时使用 `post-{id}.md`。
5. 构造 Markdown 文本内容。
6. 选择返回方式：
   - 内容已在数据库且较小：文本 Response；
   - 已有安全物理文件：FileResponse。
7. 设置 `Content-Type` 为 Markdown/纯文本的合适媒体类型。
8. 设置 `Content-Disposition`，告诉浏览器这是附件下载。
9. 返回响应。

#### 成功结果

状态码 200，响应体不是 JSON，而是 Markdown 字节内容。

#### 失败结果

- 404：文章不存在；
- 401：草稿需要登录；
- 403：登录了但无权读取；
- 500：文件在检查后、发送前意外不可读。

#### 前端如何调用

最简单的方式是创建或使用一个 `<a>`，把 href 指向下载 URL。需要 Bearer Header 时，普通导航无法加 Header，此时前端函数要使用 `fetch` 取得 Blob，再生成临时下载链接。

---

### 前端函数卡：`downloadPost`

#### 输入

文章 ID。

#### 首次出现的新浏览器概念

`Blob`：浏览器内存中的一块文件数据。

`URL.createObjectURL(blob)`：为这块临时数据生成一个浏览器可访问的临时 URL。

#### 处理顺序

1. 显示“正在准备下载”。
2. 用 `apiRequest` 或 `fetch` 请求下载接口，并携带 token。
3. 检查 `response.ok`。
4. 不调用 `response.json()`，而是读取 `response.blob()`。
5. 从响应 Header 尝试取得文件名；取不到就用 `post-{id}.md`。
6. 创建临时 `<a>`。
7. 设置 href 为 object URL，设置 download 文件名。
8. 触发点击。
9. 删除临时 `<a>`。
10. 调用 `URL.revokeObjectURL` 释放临时 URL。
11. 恢复按钮。

#### 为什么不能调用 `response.json()`

接口返回的是文件内容，不是 JSON 文本。用 JSON 解析会报错。

---

### 博客接口卡：`POST /api/v1/preferences/page-size`

#### 补充拆解

- **建议路由函数名**：`set_page_size_preference`。
- **这个后端功能可以做什么**：用一个无敏感Cookie记住列表页大小。
- **输入从哪里来**：JSON body page_size为1到50；Response参数。
- **路由函数的核心职责**：验证后设置Cookie，同时返回JSON确认。
- **处理顺序**：
  1. 验证page_size。
  2. response.set_cookie设置值。开发环境可按环境决定Secure；设置SameSite。
  3. 返回当前偏好。
- **成功返回**：200，JSON含page_size，响应带Set-Cookie。
- **失败返回**：422。
- **前端拿到结果后做什么**：设置页大小后重新加载列表；fetch若跨域且要Cookie需credentials配置。
- **本阶段仍然存在的限制**：Cookie可被删除或修改，后端每次仍校验。


#### 建议路由函数名

`set_page_size_preference`

#### 功能

用一个**不敏感的 Cookie**记住用户希望每页显示几篇文章。

#### 输入

JSON 请求体：`page_size`，取值 1—20 或你项目规定范围。

#### 处理顺序

1. Pydantic 验证 page_size。
2. 在临时 `Response` 参数上调用设置 Cookie。
3. Cookie 值只存整数文本。
4. 设置合理的 SameSite。
5. 开发环境是否 Secure 根据 HTTPS 情况决定；生产必须结合 HTTPS。
6. 返回 JSON：`{"page_size": 10}`。

#### 为什么响应既有 JSON 又有 Cookie

- JSON 让当前页面立即更新状态；
- Cookie 让后续请求或下次访问仍能读取偏好。

#### 这不是认证 Cookie

用户可删除或修改它，后端每次仍需检查范围。它只影响显示数量，不影响权限和余额。

---

### 前端函数卡：`savePageSizePreference`

#### 输入

页大小输入框的字符串值。

#### 处理顺序

1. 用 `Number()` 转成数值。
2. 用 `Number.isInteger()` 检查整数。
3. 检查范围。
4. 发送 JSON POST。
5. 如果前后端跨域且要接收/发送 Cookie，fetch 设置 `credentials: "include"`。
6. 后端 CORS 必须允许 credentials，且 Origin 不能使用 `*`。
7. 成功后把当前 `limit` 改成返回的 page_size。
8. 把 `skip` 重置为 0。
9. 重新调用 `loadPosts()`。

#### 为什么要重置 skip

原来每页 5 条且在 skip=15，改成每页 20 条后，继续使用 skip=15 会落在一个奇怪的位置。回到第一页最容易理解。

---

## 博客接口升级卡：`POST /api/v1/posts/{post_id}/reading-events`

### 这一接口在本阶段的变化
业务 JSON 不变；另外在响应 Header 中加入：

- `X-Reader-XP`；
- `X-Reader-Level`。

### 处理顺序

1. 完成原有阅读奖励事务。
2. 得到 `total_xp` 和 `level`。
3. 转成字符串写入响应头。
4. JSON 仍返回完整业务结果。

### 为什么 Header 不能替代 JSON

Header 更适合附加元数据。页面核心逻辑如果只能依赖自定义 Header，会让文档、测试和其他客户端更难理解。

### 前端如何读取

在取得 Response 后、调用 JSON 解析前后都可以读取：

```text
response.headers.get("X-Reader-XP")
```

跨域时后端还要在 CORS 中把这些 Header 放入 `expose_headers`，否则浏览器 JavaScript 看不到。

---

### 接口说明卡：`POST /api/v1/posts/{post_id}/reading-events（响应Header实验）`
- **建议路由函数名**：`create_reading_event`。
- **这个后端功能可以做什么**：在原JSON结果之外，实验X-Reader-XP和X-Reader-Level元数据。
- **输入从哪里来**：同阶段5/6；Response参数。
- **路由函数的核心职责**：业务UI仍使用JSON，Header仅作学习。
- **处理顺序**：
  1. 完成阅读事件。
  2. 把total_xp和level转字符串写入Header。
  3. 返回正常JSON。
- **成功返回**：201，JSON与Header。
- **失败返回**：原错误。
- **前端拿到结果后做什么**：API client可读取headers.get；跨域需CORS expose_headers。
- **本阶段仍然存在的限制**：不要把核心业务只放Header。

## 事件竞猜与预测市场

### 本项目本阶段施工清单

- **后端路由**：`GET /api/v1/admin/events/{event_id}/report.csv`
- **后端函数**：本阶段没有新增独立后端函数。

### 预测市场接口卡：`GET /api/v1/admin/events/{event_id}/report.csv`

#### 补充拆解

- **建议路由函数名**：`download_settlement_report`。
- **这个后端功能可以做什么**：管理员下载结算报表。
- **输入从哪里来**：event_id、current_user scopes、可选筛选。
- **路由函数的核心职责**：先验证权限和事件已结算，再流式或直接生成CSV。
- **处理顺序**：
  1. 认证并要求reports:read。
  2. 查事件并确认settled。
  3. 准备表头与行。
  4. 对以 = + - @ 开头的用户文本执行CSV公式注入防护。
  5. 小数据直接Response，大数据StreamingResponse。
- **成功返回**：200，text/csv并安全文件名。
- **失败返回**：401/403/404/409。
- **前端拿到结果后做什么**：管理页面下载按钮。
- **本阶段仍然存在的限制**：流开始后无法改状态码，因此所有可预检错误先完成。


#### 建议路由函数名

`download_settlement_report`

#### 用户动作

管理员在已结算事件页面点击“下载结算报表”。

#### 输入

- event_id；
- 当前用户；
- scope `reports:read`。

#### 后端处理顺序

1. 验证 token。
2. 检查 scope。
3. 查询事件，找不到返回 404。
4. 确认状态为 settled，否则 409。
5. 查询下注和结算结果。
6. 先准备 CSV 表头。
7. 每行只输出允许字段，例如 bet_id、user_id、option_id、stake、payout。
8. 对任何用户可控文本做 CSV 公式注入防护：以 `= + - @` 开头时不能原样让电子表格执行。
9. 小报表可一次构造；大报表使用流式生成。
10. 返回 `text/csv` 和安全文件名。

#### 成功结果

200，CSV 文件。

#### 失败结果

- 401/403：认证或权限；
- 404：事件不存在；
- 409：还未结算。

#### 前端交互

管理员页面只需要一个下载按钮和状态段落，不需要表格预览或 CSS。调用方式与 `downloadPost` 类似。

---

## 限流响应升级：`Retry-After`

当下注限流器返回 429 时，响应 Header 增加 `Retry-After`，值为建议等待秒数。

### 前端函数卡：`handleRateLimitError`

#### 输入

失败 Response 和错误 JSON。

#### 处理顺序

1. 检查状态码是否为 429。
2. 读取 `Retry-After`。
3. 无法读取时使用后端 JSON 中的默认等待秒数。
4. 禁用下注按钮。
5. 页面显示“请在 N 秒后重试”。
6. 每秒更新一次文字是可选的；初学阶段也可以只用一次 `setTimeout`。
7. 等待结束后重新启用按钮。

#### 注意

前端禁用按钮只是体验优化。真正限流始终由后端完成。

---

## 两个项目共用的权限基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`require_scopes`

# 12.1 OAuth2 Scopes：权限不是前端按钮

## 博客建议 scopes

- `posts:read`；
- `posts:write`；
- `posts:publish`；
- `users:admin`。

## 预测市场建议 scopes

- `markets:read`；
- `bets:place`；
- `events:create`；
- `events:settle`；
- `ledger:read:self`；
- `reports:read`。

### 后端依赖函数卡：`require_scopes`

#### 接收什么

FastAPI 提供的 `SecurityScopes` 和当前 token。

#### 处理顺序

1. 解码 token。
2. 取得 token 中已签发的 scopes。
3. 读取当前路由要求的 scopes。
4. 逐个检查是否都拥有。
5. 缺少时返回 403，并说明缺少权限，但不要泄露不必要内部信息。
6. 返回当前用户。

#### 为什么前端隐藏按钮不算权限控制

用户可以打开开发者工具直接发送请求。后端 scope 检查必须独立存在。

## HTTP Basic 与 dataclass 的定位

- HTTP Basic 只做一个独立诊断实验，不替代主 JWT；必须在 HTTPS 下使用。
- dataclass 做最小示例即可，不要把已经稳定的全部 Pydantic schema 重写一遍。


## 阶段 12 验收

- 下载接口的前端不调用 `response.json()`。
- Blob 临时 URL 用完会释放。
- Cookie 只保存无敏感偏好，并解释 credentials/CORS 关系。
- 自定义 Header 只做附加信息。
- 429 有稳定 JSON，并可选提供 Retry-After。
- 所有 scope 都由后端检查，页面隐藏按钮不是安全边界。

---

# 阶段 13：Settings、lifespan、代理与运行时健康检查


## 进入条件

阅读 Advanced 的：

- Settings 和环境变量；
- lifespan；
- 高级中间件；
- 子应用；
- 代理与 `root_path`；
- 模板。

## 两个项目共用的运行时基础

### 本阶段施工清单

- **后端路由**：`GET /health/live`、`GET /health/ready`、`GET /internal/version`
- **后端函数**：`get_settings`、`lifespan`、`check_database_ready`、`load_minimal_seed_data`、`create_shared_http_client / close_shared_http_client`

## 本阶段为什么不是“企业架构表演”

你只解决已经真实存在的问题：

- 数据库地址散落；
- JWT 密钥写死；
- CORS 地址写死；
- 启动资源不知道在哪里创建和关闭；
- 部署平台不知道实例是否可接收流量。

不需要一次创建十几个 `core/` 文件。可以先从一个 `config.py` 和一个清晰的 `lifespan` 开始。

---

### 后端函数卡：`get_settings`

#### 补充拆解

- **函数类型**：配置依赖
- **由谁调用**：应用创建、security、数据库、CORS、路由
- **接收什么**：环境变量和本地.env。
- **返回什么**：验证后的Settings对象。
- **内部顺序**：
  1. 读取环境变量。
  2. 按字段类型解析。
  3. 检查生产环境不能使用默认弱密钥。
  4. 返回配置对象；进程内可缓存。
- **注意事项**：任何以VITE_开头的前端环境变量都会进入浏览器，后端secret绝不能放前端配置。


#### 函数类型

配置依赖或缓存配置函数。

#### 接收什么

环境变量和可选 `.env` 文件。

#### 返回什么

验证后的 Settings 对象。

#### 建议最少字段

- `environment`；
- `database_url`；
- `secret_key`；
- `allowed_origins`；
- `upload_max_bytes`；
- `access_token_expire_minutes`；
- `app_version`。

#### 完整处理顺序

1. pydantic-settings 读取环境变量。
2. 按字段类型转换，例如字符串数字转整数。
3. 验证 allowed_origins 的形状。
4. 如果 environment 是 production，检查 secret_key 不能是教程默认值。
5. 检查 upload_max_bytes 为正数。
6. 返回对象。
7. 使用进程内缓存，避免每个请求重复读文件。

#### 一个常见误区

`.env` 不是安全保险箱。它只是本地配置文件，不能提交到 Git，生产秘密应由部署平台注入。

---

### 后端函数卡：`lifespan`

#### 补充拆解

- **函数类型**：应用生命周期上下文
- **由谁调用**：FastAPI(app lifespan)
- **接收什么**：app对象与Settings。
- **返回什么**：启动完成后yield；关闭时无业务返回。
- **内部顺序**：
  1. 启动前创建共享资源，例如HTTP client、消息发布器接口。
  2. 验证关键配置。
  3. yield让应用开始接收请求。
  4. 关闭时依次停止订阅、关闭client和连接。
- **注意事项**：每个worker都会执行自己的lifespan；不能用它自动执行一次性数据库迁移或不可逆结算。


#### 函数类型

应用生命周期上下文函数。

#### 它什么时候执行

- `yield` 之前：应用开始接收请求前；
- `yield` 之后：应用停止时。

#### 启动阶段处理顺序

1. 读取并验证 Settings。
2. 创建必须共享的客户端，例如异步 HTTP Client。
3. 把客户端放到 `app.state` 或清晰的资源容器。
4. 可执行轻量启动检查。
5. 记录应用版本和环境，但不记录 secret。
6. `yield`，开始处理请求。

#### 关闭阶段处理顺序

1. 停止接收新的内部任务。
2. 关闭 HTTP Client。
3. 关闭消息发布器或订阅连接。
4. 记录关闭完成。

#### 不应该放在 lifespan 的事情

- 每个 worker 都自动执行数据库迁移；
- 自动结算事件；
- 依赖“只执行一次”的不可逆操作。

每个 worker 都有自己的 lifespan，所以这些动作可能执行多次。

---

### 接口卡：`GET /health/live`

#### 建议函数名

`liveness_check`

#### 功能

告诉运行平台：Python 进程和 HTTP 事件循环仍然能回答请求。

#### 处理步骤

1. 不查询数据库。
2. 不访问外部网络。
3. 直接返回 `{"status": "alive"}`。

#### 为什么不能检查数据库

数据库短暂故障时，如果 liveness 失败，平台可能不断重启完全健康的 API 进程，造成更大抖动。

---

### 接口卡：`GET /health/ready`

#### 建议函数名

`readiness_check`

#### 功能

告诉负载均衡：当前实例是否准备好接收真实业务流量。

#### 处理顺序

1. 确认配置已经加载。
2. 对数据库执行最轻量的查询。
3. 为检查设置较短超时。
4. 如果实时推送是强依赖，再检查消息系统连接；若不是强依赖，可以返回 degraded 而不是完全拒绝流量。
5. 汇总依赖状态。

#### 成功返回示例

```json
{
  "status": "ready",
  "database": "ok"
}
```

#### 失败返回

503，并只返回必要状态，不泄露数据库密码、内部主机名或完整 URL。

---

### 接口卡：`GET /internal/version`

#### 建议函数名

`read_internal_version`

#### 功能

让受保护的内部页面确认当前部署版本。

#### 返回字段

- app_version；
- environment；
- commit_sha；
- build_time（可选）。

#### 不能返回

- secret_key；
- 数据库完整 URL；
- 全部环境变量；
- token。

#### 权限

放在内部子应用、内部网络或管理员 scope 下。普通博客用户页面不需要它。

---

### 前端函数卡：`checkApiReadiness`

#### 页面结构

只需：

- 一个“检查服务状态”按钮；
- 一个 `<pre>` 显示结果。

#### 处理顺序

1. 请求 `/health/live`。
2. 若网络失败，显示“无法连接进程”。
3. live 成功后请求 `/health/ready`。
4. ready 为 200，显示“服务可用”。
5. ready 为 503，解析 JSON，显示“服务运行中，但暂时不能处理业务”。

#### 为什么分两次请求

这样你可以真实观察：进程活着和数据库可用不是同一件事。

---

## Vue/原生前端配置：`API_BASE_URL`

### 为什么需要它

开发、测试、生产的后端地址可能不同。不能在十几个函数中散落 `http://127.0.0.1:8000`。

### 简单做法

- 原生阶段：一个常量；
- Vue/Vite：读取公开环境变量，例如 `VITE_API_BASE_URL`。

### 安全提醒

任何 `VITE_` 开头的变量会进入浏览器构建产物。它只能保存公开地址，不能保存 JWT 签名密钥、数据库密码或 Webhook secret。


### 后端函数卡：`check_database_ready`

**函数类型：** 就绪检查函数

**由谁调用：** ready 路由

**接收什么：** engine/Session。

**返回什么：** 布尔或诊断结果。

**内部处理顺序：**

1. 执行轻量查询。
2. 设置短超时。
3. 成功返回 ready。
4. 失败记录安全错误并返回 not ready。

**为什么要单独写这个函数：** live 只证明进程活着，ready 才说明能服务。

**重点语法或方法：** 轻量 SELECT、异常捕获。

**边界与限制：** 不能全表扫描。

### 后端函数卡：`load_minimal_seed_data`

**函数类型：** 启动初始化函数

**由谁调用：** lifespan 开始

**接收什么：** Session、环境模式。

**返回什么：** 创建数量或无。

**内部处理顺序：**

1. 只在开发/测试运行。
2. 查询种子是否存在。
3. 不存在才创建。
4. 一次 commit。

**为什么要单独写这个函数：** 本地启动后有最低数据且可重复运行。

**重点语法或方法：** 环境开关、幂等查后创建。

**边界与限制：** 生产不创建弱密码管理员。

### 后端函数卡：`create_shared_http_client / close_shared_http_client`

**函数类型：** lifespan 资源函数

**由谁调用：** lifespan

**接收什么：** Settings。

**返回什么：** 共享 client / 无。

**内部处理顺序：**

1. 启动时创建并放入 app.state。
2. 请求中复用。
3. 关闭阶段 await close。

**为什么要单独写这个函数：** 阶段 15 外部请求不应每次创建昂贵客户端。

**重点语法或方法：** app.state、async context manager。

**边界与限制：** 资源必须在关闭阶段释放。

## 阶段 13 验收

- 数据库 URL、JWT 密钥和 CORS Origin 不再散落在路由文件。
- production 使用默认弱密钥时应用拒绝启动。
- live 不依赖数据库，ready 才检查关键依赖。
- lifespan 资源有测试，进入和退出都被验证。
- 前端从一个位置读取 API base URL。
- 代理路径下 `/docs` 和接口 URL 经过真实验证。

---

# 阶段 14：WebSocket 双向实时通信


## 进入条件

完成 WebSocket 与 WebSocket 测试章节。你已经在阶段 10 学过 SSE，因此必须先回答：这个功能为什么不能继续使用 SSE + 普通 POST？

只有需要客户端在同一条长连接上频繁发消息、订阅和取消订阅时，才使用 WebSocket。

## 浏览器只需要先学这些

- `new WebSocket(url)`：开始连接；
- `socket.onopen`：连接成功；
- `socket.onmessage`：收到消息；
- `socket.send(text)`：发送字符串；
- `socket.onclose`：连接关闭；
- `socket.close()`：主动关闭；
- `socket.readyState`：确认现在能不能发送。

对象发送前使用 `JSON.stringify()`；收到字符串后使用 `JSON.parse()`。

---

## 两个项目共用的连接管理基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`ConnectionManager.connect`、`ConnectionManager.disconnect`、`ConnectionManager.broadcast`


### 后端函数卡：`ConnectionManager.connect`

#### 补充拆解

- **函数类型**：连接管理函数
- **由谁调用**：post_discussion_socket
- **接收什么**：post_id、WebSocket。
- **返回什么**：无；内部保存连接。
- **内部顺序**：
  1. 先确定项目约定：accept 只能在路由或 manager 中做一次，不能双方都做。
  2. 取得 post_id 对应的连接集合；房间不存在时创建空集合。
  3. 把当前 WebSocket 加入。加入前后可记录连接数，但日志不包含 token。
  4. 若后续发送 join_ack 失败，必须从集合移除，不能留下死连接。
- **数据结构解释**：外层用 post_id 找房间，内层保存当前连接对象。不能把用户名当唯一连接键，因为同一用户可能开两个标签页。
- **返回值为什么可以是无**：调用方关心的是 manager 内部连接状态；成功确认通过 join_ack 发给客户端，不把 Python 连接对象返回给浏览器。
- **注意事项**：所有 connect 必须有对应 disconnect；移除最后一个连接后删除空房间，避免房间字典无限增长。


#### 接收什么

post_id、WebSocket。

#### 处理步骤

1. 按项目统一位置执行 accept。
2. 如果房间不存在，创建空连接列表。
3. 把当前 socket 加入房间。
4. 避免重复加入同一对象。

#### 注意

每一次 connect 都必须有 disconnect 清理路径。

---

### 后端函数卡：`ConnectionManager.disconnect`

#### 接收什么

post_id、WebSocket。

#### 处理步骤

1. 找到房间。
2. 若 socket 在列表中则移除。
3. 房间为空则删除字典中的 post_id。
4. 不因为“连接已经不在列表”再次抛异常。

#### 为什么做成幂等清理

网络异常可能让多个错误路径都尝试清理。重复清理不应再制造新异常。

---

### 后端函数卡：`ConnectionManager.broadcast`

#### 补充拆解

- **函数类型**：连接管理函数
- **由谁调用**：评论保存成功后
- **接收什么**：post_id和公开消息。
- **返回什么**：无。
- **内部顺序**：
  1. 根据 post_id 找房间；不存在时直接结束，不是错误。
  2. 复制当前连接列表快照。复制的原因是发送过程中可能移除连接；直接一边遍历原集合一边删除会产生迭代错误或漏项。
  3. 对快照中的每个连接发送同一个公开消息对象。
  4. 单个 send 失败时记录该连接，继续发送其他连接，不能让一个坏连接中断整个房间。
  5. 遍历结束后统一移除失败连接；房间为空则删除。
- **消息对象来源**：只广播数据库 commit 后得到的公开 Comment 响应，不能广播尚未保存的用户原始文本。
- **返回值**：核心可不返回；调试或指标可返回成功数/失败数，但不能把内部 WebSocket 对象放入响应。
- **注意事项**：一个慢连接仍可能拖慢顺序广播；生产需每连接发送队列、超时和背压策略。


#### 接收什么

post_id 和公开消息对象。

#### 处理步骤

1. 复制当前连接列表快照。
2. 逐个发送 JSON。
3. 某个连接失败时记录它。
4. 本轮结束后移除失败连接。
5. 不能让一个坏连接阻止其他连接收到消息。

#### 学习版限制

内存房间只在单 worker 内有效。多 worker 或多机器需要共享消息系统。

---

## 个人博客系统

### 本项目本阶段施工清单

- **后端路由**：`WS /ws/posts/{post_id}/discussion`
- **后端函数**：本阶段没有新增独立后端函数。

### 博客 WebSocket 接口卡：`WS /ws/posts/{post_id}/discussion`

#### 补充拆解

- **建议路由函数名**：`post_discussion_socket`。
- **这个后端功能可以做什么**：让已登录用户在某篇文章的实时房间发送短消息，并立即收到其他人的消息。文章和历史评论仍通过HTTP。
- **输入从哪里来**：WebSocket路径post_id；连接认证可使用短期ticket查询参数或同源Cookie。本手册教学版可使用短期ticket，不能把长期token长期放URL。
- **路由函数的核心职责**：验证连接、加入房间、循环收消息、验证消息、保存或广播，并在断线时清理。
- **处理顺序**：
  1. 在accept前检查Origin、ticket、文章存在和用户权限。
  2. accept连接。
  3. 把连接加入post_id房间。
  4. 发送join_ack。
  5. 循环receive_json。
  6. 未知type返回system.error。
  7. message.create时检查文本长度和频率。
  8. 若设计持久化，先调用create_comment_service并commit。
  9. 数据库成功后广播comment.created。
  10. 捕获WebSocketDisconnect并移除连接。
- **成功返回**：WebSocket没有普通HTTP 200 body；成功由join_ack和后续消息表示。
- **失败返回**：认证失败可在accept前关闭；字段错误发送system.error；超大/违规可用合适关闭码。
- **前端拿到结果后做什么**：Vue/原生页面把新评论追加到讨论列表；重连后先GET /comments获取最新快照。
- **本阶段仍然存在的限制**：单worker内存ConnectionManager不能跨进程广播。


#### 建议函数名

`post_discussion_socket`

#### 用户功能

在文章详情页打开一个极简实时讨论区。历史评论仍通过 HTTP 获取，WebSocket 只传递页面打开后的新消息。

#### 为什么历史评论仍用 HTTP

HTTP 分页、缓存、错误状态和测试都更清楚。WebSocket 只负责实时增量，不应该替代所有查询。

#### 输入来源

- 路径 post_id；
- 短期连接 ticket 或同源认证 Cookie；
- WebSocket 消息 JSON。

#### 消息最小格式

```json
{
  "type": "message.create",
  "request_id": "browser-generated-id",
  "data": {"text": "你好"}
}
```

#### 后端处理顺序

1. 在 accept 前检查 Origin。
2. 验证短期 ticket。
3. 查询文章是否存在、用户是否可访问。
4. `accept()`。
5. 把连接加入该 post_id 的房间。
6. 发送 `join.ack`，告诉前端连接已进入哪个房间。
7. 循环接收 JSON。
8. 检查 `type`。
9. `message.create` 时检查 text 是字符串、去空白后非空、长度不超过上限。
10. 执行消息频率限制。
11. 若需要持久化，先写评论数据库并 commit。
12. commit 成功后广播 `comment.created`。
13. 断线时捕获 `WebSocketDisconnect`。
14. 从房间中移除连接；房间为空时删除房间键。

#### 为什么必须 commit 后广播

如果先广播“评论已创建”，随后数据库提交失败，所有页面都看见了一个数据库中不存在的评论。

#### 失败处理

- 连接前认证失败：拒绝或关闭连接；
- 消息字段错误：发送 `system.error`，说明 request_id 和错误；
- 消息过大或持续滥用：使用合适关闭码关闭；
- 单个客户端发送失败：移除该连接，不中断其他用户。

---


### 前端函数卡：`connectDiscussionSocket`

#### 什么时候调用

用户选中文章并点击“打开实时讨论”。

#### 页面最小元素

- 连接状态 `<p>`；
- 消息容器 `<section>`；
- 一个文本输入框；
- 一个发送按钮；
- 一个关闭按钮。

无需 `ul/li`，无需 CSS。

#### 处理顺序

1. 如果已有旧 socket，先关闭。
2. 通过普通 HTTP 请求历史评论。
3. 请求短期 WebSocket ticket。
4. 构造 ws/wss URL。
5. 创建 WebSocket。
6. `onopen`：显示“已连接”。
7. `onmessage`：JSON.parse；按 type 分支处理。
8. `comment.created`：创建一个 `<p>` 追加到 section。
9. `system.error`：在错误段落显示 detail。
10. `onclose`：显示“连接已关闭”。
11. 页面离开或切换文章时调用 close。

#### 发送函数 `sendDiscussionMessage`

1. 读取输入框 value。
2. `.trim()` 后为空则不发送。
3. 检查 `socket.readyState === WebSocket.OPEN`。
4. 构造消息对象。
5. JSON.stringify 后 send。
6. 不立即把消息假装为成功评论；等待服务器广播或 ack。
7. 成功确认后清空输入框。

---

## 事件竞猜与预测市场

### 本项目本阶段施工清单

- **后端路由**：`WS /ws/markets`
- **后端函数**：本阶段没有新增独立后端函数。

### 预测市场 WebSocket 接口卡：`WS /ws/markets`

#### 补充拆解

- **建议路由函数名**：`market_updates_socket`。
- **这个后端功能可以做什么**：允许一个页面通过同一连接订阅或取消多个事件，而不是为每个卡片开一条连接。这体现WebSocket双向命令的价值。
- **输入从哪里来**：连接认证可选；客户端消息type为subscribe/unsubscribe/ping，data含event_ids整数列表。
- **路由函数的核心职责**：维护当前连接的订阅集合，只推送已订阅事件的公开变化。
- **处理顺序**：
  1. 验证Origin和可选身份。
  2. accept并初始化空订阅集合。
  3. 收到subscribe时验证event_ids存在并加入集合。
  4. 收到unsubscribe时移除。
  5. 收到ping返回pong。
  6. 数据库事务commit后的领域事件到达时，只向订阅者发送pool.updated或event.settled。
  7. 断线清理。
- **成功返回**：通过ack和事件消息返回。
- **失败返回**：未知type、字段错误发送system.error；频率/数量超限可关闭。
- **前端拿到结果后做什么**：市场首页根据当前可见事件发送subscribe；列表变化时unsubscribe旧事件。
- **本阶段仍然存在的限制**：下注仍走HTTP，保留幂等、状态码和审计语义。


#### 为什么使用一条连接

市场首页可能同时显示多个事件。为每个事件开一条连接会增加资源和清理复杂度。一条连接可以让客户端发送 subscribe/unsubscribe 命令。

#### 客户端消息类型

- `subscribe`：订阅 event_ids；
- `unsubscribe`：取消；
- `ping`：检查连接。

#### 后端处理顺序

1. 验证 Origin 和可选身份。
2. accept。
3. 为当前连接创建空订阅集合。
4. 收到 subscribe：检查 event_ids 为整数列表、数量不超过上限、事件存在。
5. 加入订阅集合。
6. 返回 subscribe.ack。
7. 收到 unsubscribe：移除对应 ID。
8. 收到 ping：返回 pong。
9. 下注事务 commit 后，消息层产生 pool.updated。
10. 只向订阅该 event_id 的连接发送。
11. 断线时删除连接和订阅集合。

#### 为什么下注仍使用 HTTP

HTTP POST 已经有：

- JWT；
- 幂等键；
- 201/409/422；
- 事务错误；
- 清晰测试。

实时更新用 WebSocket，不代表所有写操作都要改成 WebSocket。

---

### 前端函数卡：`syncMarketSubscriptions`

#### 输入

旧 event ID 数组和页面现在显示的新 ID 数组。

#### 简单实现思路

不强制学习 `Set`。数据量小时用 `includes`：

1. 新数组中、旧数组没有的 ID 是新增订阅。
2. 旧数组中、新数组没有的 ID 是取消订阅。
3. 分别发送 subscribe 和 unsubscribe。
4. 收到 ack 后更新本地订阅状态。

#### 消息版本

市场更新带递增 `version`：

- 小于等于当前 version 的旧消息忽略；
- 发现版本跳号，重新 GET 事件详情；
- 完整详情成功后再继续接收增量。

## WebSocket 测试函数

每一条都要展开测试：

- `test_websocket_rejects_bad_ticket`：错误 ticket 无法进入房间；
- `test_unknown_message_type_returns_error`：连接不断开但返回明确错误；
- `test_disconnect_removes_connection`：关闭后 manager 中不残留；
- `test_comment_broadcast_happens_after_commit`：数据库失败时不广播；
- `test_market_subscription_receives_only_selected_events`：订阅 A 不会收到 B。


## 阶段 14 验收

- 能明确解释该功能为什么需要 WebSocket，而不是“因为高级”。
- 历史查询和下注仍走 HTTP。
- 前端切换页面会关闭旧连接。
- 消息有 type、request_id、data，不传随意字符串。
- 数据库 commit 之后才广播。
- 明确单 worker ConnectionManager 的限制。

---

# 阶段 15：Webhook、Callback、SDK 与边界类型最小实验


## 进入条件

阅读：

- OpenAPI callbacks；
- OpenAPI webhooks；
- 生成 SDK；
- WSGI 挂载；
- Base64 bytes；
- 严格 Content-Type；
- 高级 Python 类型。

## 本阶段定位

这些不是每个新手项目都必须使用的“高级套装”。主线只加入两个真正有意义的外部集成功能：

- 博客发布通知 Webhook；
- 预测市场受控 Oracle 结果入口。

其他内容只做最小实验，不重构全部项目。

---

## 个人博客系统

### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/admin/webhook-subscriptions`、`GET /api/v1/admin/webhook-subscriptions`、`DELETE /api/v1/admin/webhook-subscriptions/{subscription_id}`
- **后端函数**：`enqueue_webhook_event`

### 博客接口卡：`POST /api/v1/admin/webhook-subscriptions`

#### 补充拆解

- **建议路由函数名**：`create_webhook_subscription`。
- **这个后端功能可以做什么**：让管理员登记一个接收文章发布通知的外部地址。
- **输入从哪里来**：JSON body：event_types字符串列表、target_url字符串、description；admin scope。
- **路由函数的核心职责**：验证允许的事件类型和目标URL安全规则，生成订阅记录。敏感签名密钥由服务端生成并只显示一次或安全保存。
- **处理顺序**：
  1. 认证并要求admin。
  2. 只允许post.published/post.updated等白名单事件。
  3. 解析URL，只允许https或教学localhost。
  4. 拒绝环回/私网/云元数据地址，或教学版只用明确域名allowlist。
  5. 创建subscription_id和secret。
  6. 保存并返回不含完整secret的公开记录；若首次返回secret，明确只显示一次。
- **成功返回**：201，返回subscription_id、event_types、target_url、is_active、created_at；可选一次性secret。
- **失败返回**：401/403/409/422；不安全URL 400。
- **前端拿到结果后做什么**：通常是管理页配置功能，不是普通读者页面。
- **本阶段仍然存在的限制**：真正投递需要可靠队列/outbox；不能阻塞文章发布。


#### 建议函数名

`create_webhook_subscription`

#### 用户功能

管理员登记一个外部服务地址。文章发布后，系统稍后向这个地址发送通知。

#### 输入

JSON：

- `target_url`；
- `event_types`；
- `description`。

#### 后端处理顺序

1. 认证管理员并检查 scope。
2. event_types 只允许白名单，如 `post.published`、`post.updated`。
3. 解析 target_url。
4. 生产环境只允许 HTTPS。
5. 防止 SSRF：不能允许任意环回、私网和云元数据地址。学习阶段最简单可靠的是域名 allowlist。
6. 检查相同 URL 与事件组合是否已存在。
7. 服务端生成 subscription_id。
8. 服务端生成签名 secret。
9. 安全保存 secret；公开返回中不反复展示完整 secret。
10. 保存订阅并返回公开记录。

#### 成功返回

201，包含 ID、URL、事件类型、启用状态和创建时间。若课程设计为首次显示 secret，只显示这一次并明确提醒保存。

#### 失败返回

- 401/403；
- 409 重复订阅；
- 422 字段错误；
- 400 不安全 URL。

---

### 博客接口卡：`GET /api/v1/admin/webhook-subscriptions`

#### 建议函数名

`list_webhook_subscriptions`

#### 为什么增加这个接口

创建之后，管理页面需要真实查看现有订阅，不能用前端数组假装。

#### 返回内容

每项只包含：

- subscription_id；
- target_url；
- event_types；
- description；
- is_active；
- created_at。

绝不返回完整 secret。

#### 前端交互

页面只需要一个“刷新订阅”按钮、一个 section 和每项一个“停用”按钮。

---

### 博客接口卡：`DELETE /api/v1/admin/webhook-subscriptions/{subscription_id}`

#### 补充拆解

- **建议路由函数名**：`delete_webhook_subscription`。
- **这个后端功能可以做什么**：停用订阅。
- **输入从哪里来**：subscription_id、admin。
- **路由函数的核心职责**：软停用订阅，不再发送新事件。
- **处理顺序**：
  1. 查订阅。
  2. 权限检查。
  3. 设置is_active=false。
- **成功返回**：204。
- **失败返回**：401/403/404。
- **前端拿到结果后做什么**：管理页移除订阅。
- **本阶段仍然存在的限制**：历史投递记录保留审计。


#### 建议函数名

`disable_webhook_subscription`

#### 处理步骤

1. 认证授权。
2. 查订阅，找不到 404。
3. 设置 `is_active=false`。
4. 保留历史投递审计。
5. 返回 204。

#### 前端注意

204 没有 JSON。成功后重新调用列表接口，不对本地数组做未经确认的猜测。

---

### 后端业务函数卡：`enqueue_webhook_event`

#### 补充拆解

- **函数类型**：领域/outbox函数
- **由谁调用**：文章发布事务
- **接收什么**：Session、event_type、payload。
- **返回什么**：outbox记录。
- **内部顺序**：
  1. 构造唯一event_id。
  2. 把outbox记录与文章发布放在同一事务。
  3. commit后由独立worker读取并发送。
- **注意事项**：本阶段没有任务队列时，可实现outbox和手动发送命令，不用BackgroundTasks假装可靠。


#### 由谁调用

文章发布 service，在数据库事务内调用。

#### 接收什么

- Session；
- event_type；
- 公开 payload。

#### 处理顺序

1. 生成唯一 event_id。
2. 构造 outbox 记录。
3. payload 只包含接收方需要的公开字段。
4. 把 outbox 与文章发布放在同一数据库事务。
5. 不在当前 HTTP 请求里直接访问外部 URL。
6. commit 后由独立 worker 读取 outbox 并投递。

#### 为什么 BackgroundTasks 不足以保证可靠投递

进程可能在响应后、任务执行前崩溃。Outbox 记录已经持久化，可以重试和审计。

---

### 前端函数卡：`loadWebhookSubscriptions`

#### 处理顺序

1. 管理员登录后调用列表接口。
2. 清空旧 section。
3. 没有订阅时显示“暂无订阅”。
4. 每项创建一个 `<p>` 展示 URL 和事件类型。
5. 创建一个停用按钮。
6. 点击时调用 DELETE。
7. 204 成功后重新加载列表。

不需要表格、复杂弹窗或 CSS。

---

## 事件竞猜与预测市场

### 本项目本阶段施工清单

- **后端路由**：`POST /api/v1/webhooks/oracle-results`、`GET /api/v1/admin/oracle-results/{oracle_result_id}`、`POST /api/v1/admin/oracle-results/{oracle_result_id}/approve`
- **后端函数**：本阶段没有新增独立后端函数。

### 预测市场接口卡：`POST /api/v1/webhooks/oracle-results`

#### 补充拆解

- **建议路由函数名**：`receive_oracle_result`。
- **这个后端功能可以做什么**：接收受控外部服务提交的事件结果候选，不让浏览器持有共享密钥。
- **输入从哪里来**：原始请求body；Headers含时间戳、nonce、签名；Content-Type必须正确JSON。
- **路由函数的核心职责**：先验证传输安全、签名、重放和幂等，再解析业务模型；只记录待审核结果或触发受控流程。
- **处理顺序**：
  1. 严格检查Content-Type。
  2. 读取原始body bytes。
  3. 检查timestamp在允许窗口。
  4. 检查nonce未使用。
  5. 根据确定规则计算HMAC并compare_digest。
  6. 解析event_external_id、winning_option_id、occurred_at。
  7. 用oracle_event_id唯一约束检查幂等。
  8. 保存OracleResult status=pending_review。
  9. 返回接收结果。
- **成功返回**：202，返回 oracle_result_id、status=pending_review、received_at。
- **失败返回**：媒体类型错误415；签名/时间戳失败401或403；重复同内容200/202；同ID不同内容409；字段错误422。
- **前端拿到结果后做什么**：普通Vue前端不调用它；管理员页面只读取待审核结果。
- **本阶段仍然存在的限制**：收到外部结果不直接不可逆转账。管理员/规则审核后调用已有结算service。


#### 建议函数名

`receive_oracle_result`

#### 谁调用它

受控的服务器端 Oracle 服务，不是普通浏览器前端。

#### 为什么浏览器不能持有共享密钥

浏览器 JavaScript 和构建文件都能被用户查看。任何放在浏览器里的 HMAC secret 都等于公开，不能证明请求来自可信 Oracle。

#### 输入

- 原始 JSON body；
- 时间戳 Header；
- nonce Header；
- signature Header；
- 严格正确的 Content-Type。

#### 后端处理顺序

1. 检查 Content-Type 是允许的 JSON 媒体类型。
2. 读取原始 body bytes；签名验证必须基于确定的原始数据规则。
3. 解析时间戳，检查与服务器时间差在允许窗口内。
4. 检查 nonce 是否已使用。
5. 按固定拼接规则计算本地 HMAC。
6. 使用常数时间比较函数比较签名。
7. 签名通过后才解析业务字段。
8. 检查 external_event_id、winning_option_id、occurred_at。
9. 用 oracle_event_id 或外部结果 ID 做数据库唯一幂等。
10. 保存为 `pending_review`，不立即不可逆结算。
11. 返回接收回执。

#### 成功返回

202：已接收，等待审核。

字段：

- oracle_result_id；
- status；
- received_at。

#### 失败返回

- 415：Content-Type 不正确；
- 401/403：签名、时间戳或 nonce 失败；
- 409：同一外部 ID 搭配不同内容；
- 422：业务字段错误。

---

### 管理接口卡：`GET /api/v1/admin/oracle-results/{oracle_result_id}`

#### 补充拆解

- **建议路由函数名**：`get_oracle_result`。
- **这个后端功能可以做什么**：让管理员查看待审核外部结果。
- **输入从哪里来**：ID、admin scope。
- **路由函数的核心职责**：返回公开审核信息和签名验证状态，不返回密钥。
- **处理顺序**：
  1. 认证授权。
  2. 查记录。
  3. 返回。
- **成功返回**：200。
- **失败返回**：401/403/404。
- **前端拿到结果后做什么**：管理页展示并允许人工比对。
- **本阶段仍然存在的限制**：审计日志记录审核动作。


#### 功能

管理员查看待审核结果和签名验证摘要。

#### 返回什么

- 外部事件 ID；
- 候选 winning_option_id；
- occurred_at；
- status；
- received_at；
- 验签是否通过。

不返回 secret、完整签名计算材料或服务器内部密钥。

---

### 管理接口卡：`POST /api/v1/admin/oracle-results/{oracle_result_id}/approve`

#### 为什么增加审核动作

Oracle 接口只负责接收外部候选结果。管理员确认后，才调用已经测试过的结算 service。

#### 处理顺序

1. 认证并检查 events:settle scope。
2. 查询 OracleResult。
3. 确认状态为 pending_review。
4. 查询目标事件并确认可结算。
5. 调用同一个 `settle_event_service`，不要复制结算算法。
6. 结算事务成功后把 OracleResult 标为 approved。
7. 返回结算摘要。

#### 幂等

重复 approve 不得重复发放奖励。可以返回 409 或原摘要，但必须固定契约。

---

## Callback 最小实验

设计一个“生成大报告”接口时，客户端可以提交 `callback_url`。报告完成后服务端向该 URL POST 完成通知。

你只需掌握：

1. OpenAPI callback 描述的是“服务器未来会反向调用客户端”。
2. 文档描述不等于自动发送，真正 HTTP 调用仍需你实现。
3. callback_url 也有 SSRF 风险，不能任意访问。
4. 没有真实外部客户系统时，不把它列为主项目必做。

## SDK 最小实验

当前前端仍可使用普通 JavaScript fetch，不强制 TypeScript。

只完成：

1. 为每个路由设置稳定、唯一的 operationId。
2. 导出 `/openapi.json`。
3. 用生成器为一个只读接口生成客户端。
4. 对照生成函数名与 operationId。
5. 不手工大改生成文件；需要变化时更新 API 契约并重新生成。

## Base64、dataclass、高级类型、WSGI

- Base64：只做很小字节内容的 JSON 实验；普通文件继续 UploadFile/FileResponse。
- dataclass：只做内部数据结构实验，不替换全部 schema。
- Optional：理解“可为 None”和“可以不提供”不是同一件事。
- WSGI：没有遗留 Flask/Django 应用时只运行官方最小挂载示例。


## 阶段 15 验收

- Webhook 订阅列表来自真实后端，不用静态数组。
- 浏览器中没有 HMAC secret。
- 发布事务与 outbox 同事务保存。
- Oracle 有 Content-Type、时间戳、nonce、签名和幂等检查。
- 外部结果先 pending_review，再复用现有结算 service。
- SDK/Base64/WSGI 只做最小实验，没有破坏主线清晰度。

---

# 阶段 16：部署、进程、迁移、冒烟检查与独立开发验收


## 进入条件

阅读与你实际部署方式有关的 FastAPI Deployment 章节，以及 Vue 的生产构建说明。

## 两个项目共用的部署基础

### 本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`validate_required_settings`、`run_database_migrations`、`seed_initial_admin`、`smoke_check_backend`、`verify_frontend_build`、`verify_backup_restore`、`wait_for_readiness`

## 本阶段仍然前后端并行

- 后端：真实生产配置、数据库迁移、进程、日志和健康检查。
- 前端：执行真实生产构建，使用生产 API 地址，验证刷新、登录、下载、SSE/WebSocket 重连。

本阶段不新增花哨业务路由。重点是让已经完成的功能在不同进程和重启情况下仍然正确。

---


### 后端函数卡：`validate_required_settings`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 检查必填项。
2. 拒绝占位弱密钥。
3. 检查生产 CORS。
4. 失败使用非零退出码。

**为什么要单独写这个函数：** 启动前发现缺失或危险配置。

**重点语法或方法：** Settings validation、退出码。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

### 后端函数卡：`run_database_migrations`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 确认备份。
2. 执行 upgrade。
3. 检查 revision。
4. 失败停止发布。

**为什么要单独写这个函数：** 确保表结构与代码一致。

**重点语法或方法：** 迁移工具命令/函数。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

### 后端函数卡：`seed_initial_admin`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 查询是否已存在。
2. 从安全输入读取密码。
3. 哈希并创建。
4. 不打印密码。

**为什么要单独写这个函数：** 安全创建首个管理员。

**重点语法或方法：** 密码安全输入、哈希。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

### 后端函数卡：`smoke_check_backend`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 请求 live。
2. 请求 ready。
3. 请求公开列表。
4. 可选登录/me。
5. 失败非零退出。

**为什么要单独写这个函数：** 部署后验证真实 API。

**重点语法或方法：** HTTP client、超时、断言。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

### 后端函数卡：`verify_frontend_build`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 检查 index.html。
2. 检查静态资源。
3. 扫描明显 secret 名。
4. 启动静态服务请求一次。

**为什么要单独写这个函数：** 确认 Vue dist 可用且未明显泄密。

**重点语法或方法：** 文件检查、简单扫描。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

### 后端函数卡：`verify_backup_restore`

**函数类型：** 部署/运维脚本函数

**由谁调用：** CI/CD 或手工发布流程

**接收什么：** Settings、数据库/文件路径等。

**返回什么：** 成功结果或非零失败。

**内部处理顺序：**

1. 恢复到隔离库。
2. 检查关键表。
3. 运行只读 smoke。
4. 销毁隔离环境。

**为什么要单独写这个函数：** 证明备份真的可恢复。

**重点语法或方法：** 数据库恢复工具、隔离环境。

**边界与限制：** 不打印秘密，不在生产库上直接做破坏性演练。

# 16.1 必须先理解多 worker

每个 worker 都是独立 Python 进程，因此下面这些内存对象不会共享：

- 内存限流器；
- 连接管理器；
- SSE 订阅列表；
- WebSocket 房间；
- 临时 XP；
- 任何全局 dict/list。

数据库中的文章、余额和下注会共享，因为它们存储在外部数据库。

#### 实践结论

- 核心业务真相放数据库；
- 多实例限流使用共享存储；
- 多实例实时广播使用消息系统；
- 不把 worker 数量当成越多越快。

---

## 部署脚本任务卡：`run_migrations`

### 类型

独立部署命令，不是 API 路由，也不在每个 worker lifespan 中自动运行。

### 处理顺序

1. 读取生产数据库配置。
2. 输出将要迁移到的版本号，不输出密码。
3. 获取部署级互斥或确保平台只执行一次。
4. 执行向前迁移。
5. 失败时立即停止新版本发布。
6. 成功后执行 schema version 检查。

### 为什么不能由每个 API worker 启动时运行

四个 worker 可能同时修改表结构，造成锁、竞争或重复动作。

---

### 部署检查函数卡：`wait_for_readiness`

#### 谁调用

部署脚本或 CI/CD。

#### 接收什么

ready URL、最大等待时间、重试间隔。

#### 处理顺序

1. 循环请求 `/health/ready`。
2. 200 时结束成功。
3. 503 时等待后重试。
4. 网络失败时记录简短原因并重试。
5. 超过总时间后发布失败。

#### 为什么不是固定 sleep 30 秒

机器可能 3 秒就准备好，也可能 30 秒仍未准备好。主动检查比盲等更准确。

---

## 个人博客系统：部署冒烟检查

### 本项目本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`smoke_test_blog`

### 冒烟函数卡：`smoke_test_blog`

#### 目标

在新环境验证最短的真实博客闭环。

#### 处理顺序

1. 请求 live 和 ready。
2. 请求公开文章列表。
3. 登录专用 smoke author。
4. 创建一篇带唯一标题的测试文章。
5. 请求详情。
6. PATCH 修改标题。
7. 下载 Markdown，检查响应不是 JSON 且内容包含标题。
8. DELETE 文章。
9. 确认详情返回 404。
10. 清理测试数据。

#### 安全要求

- 使用专用低权限测试账户；
- 标记测试数据；
- 不使用管理员真实密码；
- 失败时也尝试清理。

---

## 事件竞猜与预测市场：部署冒烟检查

### 本项目本阶段施工清单

- **后端路由**：本阶段没有新增独立路由。
- **后端函数**：`smoke_test_prediction_market`

### 冒烟函数卡：`smoke_test_prediction_market`

#### 处理顺序

1. live/ready。
2. 登录测试用户。
3. 查询余额。
4. 获取一个专用开放测试事件。
5. 用唯一 Idempotency-Key 下注最小积分。
6. 重复同一请求，确认没有二次扣款。
7. 查询 bets 和 ledger，确认回执存在。
8. 查询余额和奖池，确认变化一致。
9. 不在生产公共事件上自动结算；结算 smoke 使用完全隔离的测试事件和管理员测试账户。

---

# 16.2 数据库兼容迁移顺序

复杂表结构变化使用扩展—迁移—收缩：

1. **扩展**：先新增兼容列或新表。
2. 部署既能读旧结构也能写新结构的应用。
3. **回填**：批量补齐旧数据。
4. 切换读取逻辑。
5. 观察稳定。
6. **收缩**：最后删除旧字段。

不要在同一次发布里先删除旧列，再部署仍读取旧列的旧 worker。

---

# 16.3 Vue 生产构建任务

## 前端任务卡：`build_frontend`

### 处理顺序

1. 设置公开的生产 `VITE_API_BASE_URL`。
2. 确认没有 secret 出现在任何 VITE_ 变量。
3. 安装锁定版本依赖。
4. 执行生产 build。
5. 检查生成 dist。
6. 在本地用静态服务器预览 dist，而不是用 dev server 冒充生产。
7. 打开浏览器 Network，确认请求指向正确后端。

### 前端验收函数卡：`verifyProductionFrontend`

手工或自动浏览器检查：

1. 首屏能加载真实列表。
2. 后端 404 时页面显示错误，不是空白。
3. 登录刷新后的行为符合 token 存储方案。
4. 下载文件成功。
5. SSE/WebSocket 断线后按项目规则重连或提示。
6. 页面离开后连接关闭。
7. 没有从打包文件中搜到数据库 URL、JWT secret 或 Webhook secret。

---

# 16.4 Docker 最低原则

- 固定 Python/Node 主版本并锁定依赖；
- 镜像中不复制 `.env`、开发数据库、上传文件或密钥；
- 生产不使用 reload；
- 尽量使用非 root 用户；
- 日志输出 stdout/stderr；
- 正确处理 SIGTERM；
- 上传文件放对象存储或持久卷；
- Vue 静态文件交给 CDN/Nginx/同域静态服务，按实际架构选择。

---

# 16.5 最终独立功能挑战

为了确认你不是只照着手册抄，最后自己为两个项目各增加一个小功能。

## 博客挑战：文章收藏

你必须自己写开发卡：

- `POST /api/v1/posts/{post_id}/favorites`；
- `DELETE /api/v1/posts/{post_id}/favorites`；
- `GET /api/v1/users/me/favorites`。

要求：

1. 登录用户才能收藏。
2. 重复收藏幂等。
3. 数据库唯一约束防止重复记录。
4. 前端详情页一个“收藏/取消收藏”按钮。
5. 页面加载详情时真实查询收藏状态。
6. 写成功、重复、未登录、文章不存在测试。

## 预测市场挑战：下注前确认摘要

不增加复杂算法，只增加实用交互：

1. 用户输入积分并选择选项。
2. 前端请求真实只读 quote 接口或本地展示当前输入摘要。
3. 显示事件问题、选项、下注积分、下注后余额预估。
4. 用户点击确认后才发 POST bets。
5. 后端仍重新检查余额、状态和 deadline。
6. 预估结果不能作为最终事务真相。

## 你必须能回答的九个问题

对任意新增功能，不看答案说清：

1. 用户做了什么？
2. HTTP 方法和路径是什么？
3. 输入来自 path、query、body、header 还是 file？
4. 路由、依赖、service 各自负责什么？
5. 校验顺序是什么？
6. 数据究竟在哪一步修改？
7. 成功返回哪些字段，前端为什么需要它们？
8. 每类失败返回什么，失败后哪些数据必须不变？
9. 前端哪个函数调用它，拿到结果后更新哪个元素？

## 阶段 16 验收

- 迁移是独立任务，不在每个 worker 启动时执行。
- live 与 ready 都用于真实部署检查。
- 两个 smoke test 调用真实后端，不使用静态数组。
- 多 worker 下没有依赖全局 dict 保存核心真相。
- Vue dist 使用正确 API 地址且不含秘密。
- 备份恢复在独立环境演练过。
- 你能独立完成至少一个小功能并写出完整开发卡。

---

# 附录 A：前后端并行路由地图

## 个人博客系统

| 阶段 | 后端方法与路径 | 同阶段前端真实动作 |
|---|---|---|
| 0 | `GET /health` | 打开页面立即检查连接 |
| 1 | `GET /api/v1/posts` | 加载真实文章按钮 |
| 1 | `GET /api/v1/posts/{post_id}` | 点击按钮加载正文 |
| 2 | `POST /api/v1/posts` | 表单创建文章并刷新列表 |
| 3 | `GET /api/v1/posts?keyword&skip&limit` | 搜索、上一页、下一页 |
| 4 | `PATCH /api/v1/posts/{post_id}` | 编辑当前文章 |
| 4 | `DELETE /api/v1/posts/{post_id}` | 删除后刷新列表 |
| 4 | `POST /api/v1/posts/import` | FormData 导入 Markdown |
| 6 | `POST /api/v1/auth/token` | 登录并保存当前标签页 token |
| 6 | `GET /api/v1/users/me` | 页面显示当前用户 |
| 8 | `GET/POST /posts/{id}/comments` | 加载和创建真实评论 |
| 10 | `GET /api/v1/posts/export.jsonl` | 触发公开数据导出 |
| 10 | `GET /api/v1/posts/events` | EventSource 接收文章更新 |
| 12 | `GET /posts/{id}/download` | Blob 下载 Markdown |
| 12 | `POST /preferences/page-size` | 保存页大小 Cookie |
| 13 | `GET /health/live`、`/ready` | 页面区分存活与就绪 |
| 14 | `WS /ws/posts/{id}/discussion` | 真实实时讨论 |
| 15 | Webhook subscription CRUD | 管理页面真实加载订阅 |
| 16 | 原有全部路由 | 生产 build 与 smoke test |

## 事件竞猜与预测市场

| 阶段 | 后端方法与路径 | 同阶段前端真实动作 |
|---|---|---|
| 0 | `GET /health` | 检查后端连接 |
| 1 | `GET /api/v1/events` | 加载事件按钮 |
| 1 | `GET /api/v1/events/{event_id}` | 显示选项和池子 |
| 2 | `POST /api/v1/events` | 创建真实内存事件 |
| 2 | `POST /events/{id}/bets` | 提交真实下注 |
| 3 | `GET /events?keyword&status&skip&limit` | 筛选和翻页 |
| 4 | `PATCH /events/{id}` | 编辑事件 |
| 4 | `POST /events/{id}/close` | 关闭后禁用下注 |
| 4 | `POST /events/{id}/cancel` | 取消并刷新状态 |
| 6 | 认证与管理员路由 | 登录、显示身份、受保护操作 |
| 8 | 余额、下注、账本、结算、退款 | 页面真实刷新所有事务结果 |
| 10 | `GET /events/{id}/stream` | SSE 更新市场详情 |
| 12 | `GET /admin/events/{id}/report.csv` | 下载 CSV 报表 |
| 14 | `WS /ws/markets` | 一条连接订阅多个事件 |
| 15 | Oracle webhook/admin review | 管理页读取待审核结果 |
| 16 | 原有全部路由 | 生产 smoke test 与重连检查 |

---

# 附录 B：JavaScript 最小词典——只解释手册真正使用的名称

| 名称 | 白话解释 | 第一次使用 |
|---|---|---|
| `querySelector` | 按 id 或标签找到一个页面元素 | 阶段 0 |
| `textContent` | 把内容当普通文字显示，不执行 HTML | 阶段 0 |
| `createElement` | 创建按钮、段落等元素 | 阶段 1 |
| `append` | 把新元素放进容器 | 阶段 1 |
| `addEventListener` | 监听点击或表单提交 | 阶段 0 |
| `preventDefault` | 阻止表单自动刷新页面 | 阶段 2 |
| `fetch` | 向真实后端发 HTTP 请求 | 阶段 0 |
| `response.ok` | 判断状态码是不是 2xx | 阶段 0 |
| `response.status` | 读取 200、404、422 等状态码 | 阶段 0 |
| `response.json()` | 把 JSON 响应解析成对象 | 阶段 0 |
| `response.blob()` | 把文件响应读取成 Blob | 阶段 12 |
| `JSON.stringify` | 把对象转成 JSON 请求字符串 | 阶段 2 |
| `FormData` | 同时发送文件和文字字段 | 阶段 4 |
| `URLSearchParams` | 安全拼查询参数或表单编码 | 阶段 3/6 |
| `sessionStorage` | 当前标签页暂存 token；关闭页即清理 | 阶段 6 |
| `setTimeout` | 延迟一次执行 | 阶段 12 |
| `EventSource` | 接收服务器单向 SSE | 阶段 10 |
| `WebSocket` | 浏览器与服务器双向长连接 | 阶段 14 |
| `Blob` | 浏览器内存中的文件数据 | 阶段 12 |
| `createObjectURL` | 给 Blob 生成临时下载地址 | 阶段 12 |
| Vue `ref` | 可让模板自动跟随变化的值 | 阶段 9 |
| `v-for` | 根据真实响应数组生成元素 | 阶段 9 |
| `v-model` | 输入框值和变量同步 | 阶段 9 |
| `onMounted` | 组件显示后加载真实接口 | 阶段 9 |
| `onUnmounted` | 离开页面时关闭 SSE/WS | 阶段 10/14 |

---

# 附录 C：后端函数到底放哪一层

| 函数正在做什么 | 推荐位置 | 例子 |
|---|---|---|
| 读取 HTTP 参数、选择状态码 | router | `list_posts` |
| 取得当前用户、查资源或分页参数 | dependency | `get_current_user`、`get_post_or_404` |
| 执行业务顺序和事务 | service | `place_bet_service` |
| 纯计算或清理 | 普通函数 | `normalize_tags` |
| 数据库增删查 | 小项目可由 service 直接做；复杂后再 repository | 查询 Post |
| 请求/响应字段 | schema | `PostCreate`、`PostSummary` |
| 数据库表 | model | `Post`、`Bet`、`LedgerEntry` |
| 所有请求共同包裹逻辑 | middleware | request id、耗时日志 |
| 启动和关闭共享资源 | lifespan | HTTP Client、消息连接 |

## 一个简单判断方法

问自己：“把 HTTP 拿掉后，这个函数还有没有意义？”

- 仍然有意义的下注、结算、标签清理通常是业务/纯函数。
- 专门读取 Header、Cookie、Request 的通常是依赖或路由。

---

# 附录 D：每实现一项功能前先填写

```text
用户在页面做什么：
后端方法与路径：
建议路由函数名：
输入分别来自哪里：
需要哪些依赖函数：
真正业务函数叫什么：
第一步判断什么：
第二步判断什么：
数据在哪一步才允许修改：
成功状态码：
成功返回每个字段及其前端用途：
可能的 4xx：
失败后哪些数据必须保持不变：
前端函数名：
前端要找到哪些元素：
fetch 的 URL、method、headers、body：
成功后更新哪个元素：
失败后显示在哪里：
当前阶段已知限制：
```

如果这张卡仍有一句写成“处理相关逻辑”，说明还没有拆清楚，先不要写代码。

---

# 附录 E：最终完成标准

你不需要背所有库名，但应该能做到：

1. 从页面动作画出 fetch → route → dependency → service → database → response → DOM 的完整箭头。
2. 能用具体数据解释分页，而不是只背 `[skip:skip+limit]`。
3. 知道搜索用普通 `in` 就够了，不为项目手写 KMP。
4. 每个响应字段都能说出前端为什么需要。
5. 写操作在所有校验通过前不修改状态。
6. 事务失败后不会留下半条业务。
7. 前端永远从真实 API 取业务数据，不用静态数组代替。
8. HTML 简单、无 CSS 也能完整操作项目。
9. 新 API 或浏览器方法第一次出现时，能用自己的话解释它。
10. 能脱离手册独立写出一个小功能的完整开发卡。

---

# 附录 F—H 使用说明

下面三份核对表保留了两份原稿中最有价值的“逐章自检”部分，用来确认你是否真正读懂官方章节。表格中出现 `UUID`、`Decimal`、Base64、dataclass 等名称，不代表两个主线项目必须使用它们；本手册核心项目仍遵循“能用普通整数、字符串和明确模型完成，就不为了展示技巧增加类型”的原则。只有当官方章节本身要求你认识某个类型时，才把它作为小型独立练习。

# 附录 F：FastAPI Tutorial 逐章知识点核对表

这份表不是官方正文的替代品。用途是：你读完一页后，对照“必须会”逐项自问；答不上来就回到对应标题，而不是带着空洞的“看过了”进入作业。

## F1. 从第一步到额外数据类型

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 1 | 第一步 | 安装方式与可选依赖；`fastapi dev`；应用 entrypoint；`FastAPI` 实例；路径操作装饰器与函数；常见 HTTP 方法；JSON 返回；Swagger UI、ReDoc、`openapi.json`；OpenAPI 与 JSON Schema 的关系。 |
| 2 | 路径参数 | 从类型注解解析/校验/转换路径值；路由声明顺序；`Enum` 预定义值；获得枚举值；带 `/` 的路径参数及 `:path` 转换器。 |
| 3 | 查询参数 | 非路径参数如何成为 query；默认值、可选值、必填值；字符串到 bool 等类型转换；同一路由混用 path/query；不依赖参数排列顺序。 |
| 4 | 请求体 | `BaseModel` 字段、默认/可选；请求体与 path/query 同时声明；模型属性与 `model_dump()`；编辑器支持；FastAPI 如何用模型生成 JSON Schema、校验并写入 OpenAPI。 |
| 5 | 查询参数和字符串校验 | `Annotated` 推荐写法；`Query` 的 min/max length、pattern、alias、deprecated、include_in_schema；必填但可为 None；查询参数列表与默认值；自定义标题/描述；禁止额外 query 字段的模型配置。 |
| 6 | 路径参数和数值校验 | `Path` 元数据；函数参数排序与 `*`；`ge/gt/le/lt`；浮点边界；理解 Python 默认参数规则与 FastAPI 参数来源是两层问题。 |
| 7 | 查询参数模型 | 把分页/筛选组合成 Pydantic 模型；用 `Query()` 声明模型；复用模型；`extra="forbid"` 的收益与兼容代价。 |
| 8 | 请求体 - 多个参数 | 多个 Pydantic body 参数如何形成带键 JSON；用 `Body()` 把标量放入 body；`embed=True` 改变单模型 body 形状；path/query/body 自动识别。 |
| 9 | 请求体 - 字段 | `Field` 给模型内部字段加约束和元数据；`Annotated`；字段约束进入 JSON Schema；Field 是 Pydantic 而非 FastAPI 的函数。 |
| 10 | 请求体 - 嵌套模型 | `list/set/dict` 字段；子模型、深层嵌套、模型列表；set 去重与 JSON 序列化；任意 dict body；编辑器对嵌套结构的补全。 |
| 11 | 声明请求示例数据 | `model_config.json_schema_extra`；`Field(examples=...)`；Path/Query/Header/Cookie/Body/Form/File 示例；JSON Schema 的 `examples` 与 OpenAPI 特定 `openapi_examples` 的位置、结构和 Swagger UI 支持差异。 |
| 12 | 额外数据类型 | `UUID`、`datetime/date/time/timedelta`、`frozenset`、`bytes`、`Decimal` 的输入转换、文档和输出；时间与金额类型为何优于随意字符串/float。 |

## F2. 从 Cookie/Header 到更新数据

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 13 | Cookie 参数 | 用 `Cookie()` 显式声明请求 Cookie；与 query 参数区分；`Annotated` 写法；缺失与可选。 |
| 14 | Header 参数 | `Header()`；下划线到连字符自动转换及 `convert_underscores`；重复 Header 接收为列表；Header 大小写不敏感；某些代理对下划线名称的限制。 |
| 15 | Cookie 参数模型 | 多个 Cookie 收进 Pydantic 模型；`Cookie()` 标记来源；复用与禁止额外字段；模型字段名如何映射 Cookie。 |
| 16 | Header 参数模型 | 多个 Header 收进模型；复用、约束、禁止额外 Header；下划线转换；重复值；为什么实际安全认证优先内置 security 工具。 |
| 17 | 响应模型 - 返回类型 | 返回类型与 `response_model`；输出验证、文档、过滤；内部对象比公开模型字段多时的安全收益；`Any`/Response 特例；`response_model_include/exclude` 的局限；数据模型优先于临时字段掩码。 |
| 18 | 更多模型 | 输入/输出/数据库模型分离；继承减少重复；`UserIn/UserOut/UserInDB`；Union 响应；模型列表和任意 dict；避免重复模型又不泄密。 |
| 19 | 响应状态码 | 装饰器 `status_code`；`fastapi.status` 命名常量；状态码进入 OpenAPI；哪些状态不允许响应体；201/204 等语义。 |
| 20 | 表单数据 | `Form()`；`application/x-www-form-urlencoded` 与 JSON body 的差别；`python-multipart` 依赖；一个请求不能同时把同一 body 当 JSON 与表单解析。 |
| 21 | 表单模型 | Pydantic 模型接收 Form；版本要求；文档展示；`extra="forbid"` 拒绝未声明表单字段。 |
| 22 | 请求文件 | `File()` 接收 `bytes` 与 `UploadFile` 的差别；spooled file、文件元数据、async 方法与底层 file；可选/多文件；附加元数据；multipart 的原因。 |
| 23 | 请求表单与文件 | 同一 multipart 请求组合 `File` 与 `Form`；不能同时期待 JSON body；前端需用 FormData。 |
| 24 | 处理错误 | `raise HTTPException` 而非 return；自定义 detail/Header；安装异常处理器；复用 Starlette/FastAPI 默认处理器；`RequestValidationError` 与 Pydantic `ValidationError` 的客户端/服务端含义；覆盖默认处理器。 |
| 25 | 路径操作配置 | `status_code`、tags、summary、description、函数 docstring、response_description、deprecated、operation_id；operationId 必须唯一，生成客户端前保持稳定。 |
| 26 | JSON 兼容编码器 | `jsonable_encoder` 把模型、datetime 等转换成 JSON 兼容 Python 结构；它不直接返回 Response，也不是数据库事务工具。 |
| 27 | 请求体 - 更新数据 | PUT 替换语义；PATCH 部分更新；`model_dump(exclude_unset=True)`；`model_copy(update=...)`；显式 null 与未提供的区别；用 `jsonable_encoder` 存兼容数据。 |

## F3. 依赖、安全、CORS 与数据库

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 28 | 依赖项 | 依赖就是可调用对象；参数声明与路径函数相同；FastAPI 执行并注入结果；依赖需求进入 OpenAPI；同步/异步自由组合；常见用途：共享逻辑、Session、安全。 |
| 29 | 类作为依赖项 | 类、函数、实例都可调用；FastAPI 可调用类构造器；`Annotated[CommonQueryParams, Depends()]` 的简写推断；何时用实例配置而非全局变量。 |
| 30 | 子依赖项 | 依赖可以继续依赖；FastAPI 构建依赖树；单请求默认缓存同一依赖值；`use_cache=False` 重新执行。 |
| 31 | 路径操作装饰器依赖项 | `dependencies=[Depends(...)]` 适合只需执行、不需返回值；依赖仍可抛错与包含子依赖；可在 APIRouter/全局层使用；不要用自定义 Header 重新发明标准认证。 |
| 32 | 全局依赖项 | `FastAPI(dependencies=[...])` 作用于全部路径；与装饰器依赖执行方式相同；全局策略要谨慎，公开健康端点可能需要例外架构。 |
| 33 | 使用 yield 的依赖项 | yield 前获取资源、yield 值、yield 后退出；`try/finally`；子依赖退出顺序；异常传播；与上下文管理器关系；清理时机和流式响应边界。 |
| 34 | 安全性 | OAuth2、OpenID Connect 与不同 flow 的概念；FastAPI security 工具如何集成 OpenAPI；先理解标准，不手写随机 Header 方案。 |
| 35 | 安全 - 第一步 | `OAuth2PasswordBearer(tokenUrl=...)`；Bearer 提取；401；Authorize 按钮；`tokenUrl` 是相对 URL；password flow 登录表单由后续端点实现。 |
| 36 | 获取当前用户 | security 依赖可组成子依赖；用 token 查用户；`User` 响应模型；当前用户注入路由；伪 token 示例只用于理解流程。 |
| 37 | 简单 OAuth2 Password/Bearer | `OAuth2PasswordRequestForm`；用户名密码表单；认证函数；Bearer token 响应；active user；401/400 错误；示例明文/假 token 仍不安全。 |
| 38 | 密码哈希 + JWT | `pwdlib` 推荐哈希；dummy hash；PyJWT；`sub`、`exp`、UTC；密钥生成与环境变量；捕获无效 token；`WWW-Authenticate`；不要把教程固定密钥用于生产。 |
| 39 | 中间件 | 请求前/响应后处理；`@app.middleware("http")` 与 `call_next`；耗时 Header 示例；多中间件嵌套顺序；CORS Header 暴露；中间件与 yield 依赖/后台任务的相对时序。 |
| 40 | CORS | Origin 三元组；简单请求与 OPTIONS 预检；显式 Origin；通配符与 credentials 限制；allow_origins/methods/headers/credentials/expose_headers/max_age；CORS 不是服务器认证。 |
| 41 | SQL 数据库 | FastAPI 不绑定数据库；SQLModel/SQLAlchemy/Pydantic 关系；SQLite 教学与生产 DB；表模型、Engine、create tables、Session yield 依赖、CRUD、分页；多模型区分 table/create/public/update；防止私密字段泄漏。 |

### A4. 大型应用、流、任务、文档、测试与调试

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 42 | 更大的应用 - 多个文件 | Python 包与 `__init__.py`；绝对/相对导入；`APIRouter`；prefix/tags/dependencies/responses；`include_router`；避免名称冲突；路由器嵌套路由器；同一路由器多次挂载；pyproject entrypoint。 |
| 43 | 流式传输 JSON Lines | JSONL 每行独立 JSON；路径函数 `yield`；同步/异步 iterable 和返回类型；Pydantic 验证/序列化每项；客户端按行消费；与单个 JSON 数组的内存/延迟差异。 |
| 44 | SSE | `EventSourceResponse`；每个 yield 项进入 `data`；`ServerSentEvent` 的 event/id/retry/comment；原始数据；浏览器 `EventSource`；Last-Event-ID 恢复；POST SSE；版本要求和单向语义。 |
| 45 | 后台任务 | `BackgroundTasks` 参数与 `add_task`；普通/async 任务；依赖中也可追加；响应发送后执行；小任务适用，重计算/多进程可靠任务应使用 Celery 等外部系统。 |
| 46 | 元数据和文档 URL | title/summary/description/version/terms/contact/license；tag 元数据和顺序；OpenAPI URL、docs_url、redoc_url；关闭文档不等于访问控制。 |
| 47 | 前端 | FastAPI 官方全栈模板的存在与用途；后端 OpenAPI 可支持前端/客户端；本页不是完整前端课程。 |
| 48 | 静态文件 | `StaticFiles`；`app.mount()`；name；静态应用是独立子应用，不是普通 APIRouter；目录与 HTML 模式基础。 |
| 49 | 测试 | `TestClient` 基于 HTTPX；pytest 普通函数；请求/响应断言；测试函数可普通 def；安装 httpx；分离应用对象便于导入测试。 |
| 50 | 调试 | 从 Python 文件调用 Uvicorn；`if __name__ == "__main__"`；导入模块时为何不启动；VS Code/PyCharm 断点；开发 server 与调试入口。 |

---

# 附录 G：FastAPI Advanced 逐章知识点核对表

## G1. 高级响应与依赖安全

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 1 | 流式数据 | JSON 可结构化数据优先 JSONL；字符串/bytes 用 StreamingResponse；同步/异步 `yield`；类型注解可选；原样数据块；自定义 StreamingResponse 子类；文件读取与 async 边界；`yield from`。 |
| 2 | 路径操作高级配置 | 自定义 operationId；用路由函数名生成时的唯一性；从 OpenAPI 排除；扩展 OpenAPI path operation；自定义响应/请求 schema 的高级入口。 |
| 3 | 额外的状态码 | 同一路径按结果返回不同状态；直接 `JSONResponse(status_code=...)`；装饰器默认状态与实际响应；额外状态要同时写入 `responses` 文档。 |
| 4 | 直接返回响应 | 返回 `Response` 或子类；FastAPI 不再自动转换/验证/文档化内容；`jsonable_encoder` + JSONResponse；何时应保留 response_model。 |
| 5 | 自定义响应 | Response 基类；HTML/PlainText/Redirect/Streaming/File/ORJSON 等响应；`response_class` 文档与默认；直接 Response 覆盖；默认响应类；自定义响应类和 `render()`；媒体类型/charset。 |
| 6 | OpenAPI 附加响应 | `responses` 字典；错误模型；content/media type；Header；多种媒体类型；复用预定义响应；与 response_model/default response 合并。 |
| 7 | 响应 Cookies | 临时 `Response` 参数上 `set_cookie` 后仍可返回普通数据；直接 Response 也可设置；响应模型仍执行；Cookie 安全属性需自行设计。 |
| 8 | 响应头 | 临时 Response 参数设置 Header；直接 Response 设置；自定义 `X-` Header；跨域前端读取需要 expose_headers；标准专用 Header 优先标准语义。 |
| 9 | 更改响应状态码 | 通过 Response 参数动态改 `status_code`；最后执行的依赖/路径代码决定值；OpenAPI 仍主要描述装饰器默认，额外状态需显式文档。 |
| 10 | 高级依赖项 | 可调用实例参数化依赖；`__call__` 与构造参数区别；yield 依赖 + StreamingResponse 历史/当前行为；`Depends(scope="function"/"request")`；提前清理的适用条件；不要在 yield 后吞异常。 |
| 11 | 高级安全 | 它是安全教程上的附加入口；先完成教程安全章节；按实际需求选择 OAuth2 scopes 或 HTTP Basic，不是每个项目都要全用。 |
| 12 | OAuth2 作用域 | scopes 与 OpenAPI；token 中 scope 字符串；`Security` 与 `SecurityScopes`；依赖树累积所需 scopes；验证 token 数据形状和权限；登录请求 scope 不能越权；文档 Authorize 展示。 |
| 13 | HTTP Basic | `HTTPBasic` 与 credentials；401 + `WWW-Authenticate: Basic`；用户名/密码常数时间比较；dummy bytes；必须配 HTTPS；Base64 不是加密。 |
| 14 | 直接使用 Request | Request 可与正常验证参数同时使用；直接读取 client、headers、body 等；直接获取的数据不自动验证、转换或进入 OpenAPI。 |
| 15 | 使用数据类 | 标准 `dataclasses.dataclass` 可用于请求/响应/依赖；FastAPI 内部仍借助 Pydantic；嵌套 dataclass；何时 BaseModel 功能更完整。 |

## G2. 中间件、应用边界、实时与测试

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 16 | 高级中间件 | `HTTPSRedirectMiddleware`、`TrustedHostMiddleware`、`GZipMiddleware` 的作用与配置；ASGI 中间件通用性；压缩最小大小/压缩级别；可信 Host 通配规则。 |
| 17 | 子应用 - 挂载 | `FastAPI` 子应用；独立 OpenAPI/docs；mount 路径；自动处理 `root_path`；lifespan 只在主应用的官方限制。 |
| 18 | 使用代理 | 转发头与可信代理；HTTPS 重定向；剥离/不剥离路径前缀；ASGI `root_path`；CLI `--root-path`；OpenAPI servers；代理与应用分别负责什么。 |
| 19 | 模板 | `Jinja2Templates`、Request、TemplateResponse；模板目录、context、url_for、静态文件；模板/Starlette 版本接口演进；服务端模板与 API/Vue 是不同渲染路径。 |
| 20 | WebSockets | 接受连接、收发 text/json/bytes、关闭；依赖/Query/Cookie 可用于 WS；`WebSocketException` 与 policy violation；多客户端 ConnectionManager；`WebSocketDisconnect`；内存列表只单进程。 |
| 21 | 生命周期事件 | 应用启动前/关闭时资源；`FastAPI(lifespan=...)`；`@asynccontextmanager`；yield 前后；旧 startup/shutdown 弃用且不能与 lifespan 混用；ASGI Lifespan；子应用限制。 |
| 22 | 测试 WebSockets | `TestClient` 上下文；`websocket_connect`；send/receive；WebSocket 测试使用普通 def；测试异常/关闭；依赖环境。 |
| 23 | 测试 lifespan/startup/shutdown | `with TestClient(app)` 才触发 lifespan；进入上下文前、内、后分别断言资源状态；确保清理路径被测。 |
| 24 | 覆盖测试依赖项 | `app.dependency_overrides[original] = override`；替换外部认证/收费服务；测试后清空；覆盖的是 callable 身份；避免全局状态污染其他测试。 |
| 25 | 异步测试 | pytest anyio 标记；HTTPX AsyncClient + ASGITransport；异步测试不能直接用同步 TestClient 模式混淆；lifespan 可能需单独管理；调用其他 async 函数。 |
| 26 | 设置和环境变量 | `pydantic-settings`；BaseSettings 类型转换；`.env`；`SettingsConfigDict`；依赖注入 Settings；`@lru_cache`；测试 override；环境变量嵌套/优先级概念；不要提交真实秘密。 |

## G3. OpenAPI 集成、遗留系统与特殊类型

| # | 官方章节 | 读完必须会 |
| ---: | --- | --- |
| 27 | OpenAPI 回调 | 客户端提供 callback URL；回调路径表达式；单独 APIRouter 只用于生成 OpenAPI；将 callback router 附到路径操作；理解实际发送逻辑仍需自己实现。 |
| 28 | OpenAPI 网络钩子 | OpenAPI 3.1 Webhooks；`app.webhooks` 描述你的应用将主动发出的请求；与普通入口路由和 callback 的区别；模型与文档。 |
| 29 | 包含 WSGI | `WSGIMiddleware` 挂 Flask/Django 等；mount 路径；WSGI 同步限制仍存在；用于渐进迁移，不会自动把遗留应用变异步。 |
| 30 | 生成 SDK | OpenAPI Generator 等工具；TypeScript 客户端示例；模型/operationId 会影响生成函数名；预处理 OpenAPI；标签；生成代码版本化与再生成策略。 |
| 31 | 高级 Python 类型 | 在不能使用 `|` 的位置用 `Union`；`Optional[T]` 真正表示 `T | None`，不等于“参数可省略”；默认值才决定是否可省略。 |
| 32 | JSON Base64 bytes | JSON 不能直接携带原始 bytes；Base64 有体积成本；优先文件上传/下载；Pydantic `val_json_bytes`、`ser_json_bytes`；输入/输出模型配置一致性。 |
| 33 | 严格 Content-Type | JSON body 的媒体类型检查；从 FastAPI 0.132.0 起默认执行严格检查；错误或缺失媒体类型应被拒绝；只有为兼容遗留客户端时才考虑 `FastAPI(strict_content_type=False)`，并测试代理/客户端的实际行为。 |

---

# 附录 H：Vue 3 快速上手与迁移知识点核对表

| 部分 | 必须会 |
| --- | --- |
| 线上尝试 | 知道 Playground、JSFiddle、StackBlitz 分别适合无安装体验、原始 HTML、完整构建环境；正式项目仍需本地可复现环境。 |
| 创建应用前提 | 熟悉命令行；安装官方页面要求范围内的 Node.js；在正确父目录运行脚手架。 |
| `npm create vue@latest` | 这是官方 `create-vue`；能解释 TypeScript、JSX、Router、Pinia、Vitest、E2E、ESLint、Prettier 的问题；不知道时先 No，不一次引入没学过的库。 |
| 运行与构建 | `npm install`、`npm run dev`、`npm run build`；dist 是生产构建，不用 Vite dev server 上生产。 |
| 默认风格 | 官方生成示例偏组合式 API + `<script setup>`；本手册统一使用这一风格，避免初学期同时维护 Options API 心智模型。 |
| CDN 全局构建 | `<script>` 暴露全局 `Vue`；设置简单但不能写 SFC；适合作为原生页面到 Vue 的桥。 |
| CDN ES 模块 | `<script type="module">` 直接 import；浏览器原生模块；可用 import maps 把 `vue` 映射到 CDN ESM；确认浏览器支持。 |
| 拆分模块 | 组件/模块可放独立 JS 文件；ES module 必须经 HTTP 服务，不能 `file://` 双击；模板字符串方案只作过渡。 |
| SFC | `.vue` 文件把 template/script/style 组合为组件；需要构建工具；本手册即使不用 CSS，也保留清晰组件边界。 |
| 响应式 | `ref` 适合标量/可替换值，脚本中访问 `.value`；`reactive` 适合对象；不要随意解构导致响应性丢失。 |
| 模板 | 插值默认文本转义；`v-bind`/`:` 绑定属性；`v-on`/`@` 绑定事件；模板只写表达式；避免带副作用的模板函数。 |
| 条件/列表 | `v-if` 控制创建销毁，`v-show` 控制显示；`v-for` 使用稳定业务 key；不要依赖数组下标维持组件状态。 |
| 表单 | `v-model` 是值与事件的语法糖；number/trim/lazy modifier 要理解转换；服务端仍需验证。 |
| 组件 | Props 向下、事件向上；组件名/注册；不要让所有组件直接改全局对象；API 调用集中 service/composable。 |
| 生命周期 | `onMounted` 适合连接浏览器资源，`onUnmounted` 清理 timer/SSE/WebSocket/监听；生命周期钩子注册应同步发生。 |
| 安全 | `v-html` 不会自动安全；永不渲染未消毒的用户 HTML；前端环境变量会进入构建产物，不能保存秘密。 |

---

# 官方参考入口
- FastAPI Tutorial：<https://fastapi.tiangolo.com/zh/tutorial/>
- FastAPI Advanced：<https://fastapi.tiangolo.com/zh/advanced/>
- FastAPI Deployment：<https://fastapi.tiangolo.com/zh/deployment/>
- Vue 3 Quick Start：<https://cn.vuejs.org/guide/quick-start>
- MDN Fetch：<https://developer.mozilla.org/docs/Web/API/Fetch_API>
- SQLModel：<https://sqlmodel.tiangolo.com/>
