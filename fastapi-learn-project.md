# FastAPI 渐进式全栈架构与实战重构指南

本指南对 FastAPI 官方文档进行深度解构，配合全面的底层原理解析，采用双主线项目（个人博客系统、事件竞猜与预测市场）渐进式地带领您从零构建一个企业级的高性能异步全栈应用。

---

## FastAPI 官方文档学习路径与本手册学习时机对照表

请在阅读并掌握 FastAPI 官方文档（Tutorial 及 Advanced 部分）对应的章节后，再行阅读本手册中的对应模块，以获得平滑的知识迁移体验。

```
[ 官方文档：Tutorial - User Guide ]
       │
       ├─► First Steps, Path Parameters, Query Parameters, Request Body ──► [ 模块一：基础路由与文件渲染 ]
       │
       ├─► Body - Fields, Nested Models, Extra Data, Form Data, Files ────► [ 模块二：数据验证与元数据解析 ]
       │
       ├─► Dependencies (Intro, First Steps, Sub-deps, Yield) ────────────► [ 模块三：依赖注入的高阶应用 ]
       │
       ├─► Security (Simple OAuth2, JWT access tokens, Get Current User) ──► [ 模块四：博主安全与数字验签 ]
       │
       └─► SQL (Relational) Databases ────────────────────────────────────► [ 模块五：SQLAlchemy 异步持久化 ]
       
[ 官方文档：Advanced User Guide ]
       │
       └─► WebSockets, Advanced Middleware, Lifespan Events, Settings ────► [ 模块六：实时并发与生产级部署 ]
```

---

## 目录
- [模块一：基础框架与 Markdown 文件读取渲染 (Routing & Static File)](#模块一基础框架与-markdown-文件读取渲染-routing--static-file)
- [模块二：Pydantic 约束、Markdown 安全上传与元数据解析 (Data & Form)](#模块二pydantic-约束markdown-安全上传与元数据解析-data--form)
- [模块三：依赖注入的应用——读者 XP 追踪器与防刷限流 (Dependencies)](#模块三依赖注入的应用读者-xp-追踪器与防刷限流-dependencies)
- [模块四：安全保护——博主后台 JWT 认证与防篡改数字签名 (Security & JWT)](#模块四安全保护博主后台-jwt-认证与防篡改数字签名-security--jwt)
- [模块五：异步 ORM 持久化风暴 (SQLAlchemy 2.0 + SQLite)](#模块五异步-orm-持久化风暴-sqlalchemy-20--sqlite)
- [模块六：实时并发——WebSocket 弹幕大屏与生产部署 (WebSockets & Deploy)](#模块六实时并发websocket-弹幕大屏与生产部署-websockets--deploy)

---

## 模块一：基础框架与 Markdown 文件读取渲染 (Routing & Static File)

### 1. 深度补充学习与底层原理解析

#### 1.1 ASGI 协议与 WSGI 协议的性能断代
在传统的 Python Web 开发中，**WSGI (Web Server Gateway Interface)**（如 Flask、Django）采用的是同步阻塞式架构。每个传入的 HTTP 连接都会被分配给一个独立的线程。当遇到 I/O 操作（例如从磁盘读取 Markdown 文件、查询数据库等）时，该线程会被操作系统挂起，直到 I/O 数据就绪。这种模式在应对海量并发连接（如长连接、高频轮询）时，会由于线程上下文切换（Context Switch）的开销以及线程数量限制而迅速达到物理瓶颈。

**ASGI (Asynchronous Server Gateway Interface)** 是 WSGI 的超集，是 FastAPI 实现极高性能的核心基石。它运行在 Uvicorn 等高性能 ASGI 服务器上，底层基于 Python 的 `asyncio` 事件循环（Event Loop）。当一个异步路由遇到 `await` 时，它会主动将 CPU 的控制权让渡给事件循环，从而使单线程在等待 I/O 就绪的同时，可以继续接收和处理其他用户的 HTTP 请求。

在底层，ASGI 将 HTTP 请求交互解构为一系列离散的“事件”流（例如 `http.request`、`http.response.start`、`http.response.body`）。基于 asyncio 的事件循环通过操作系统底层的多路复用机制（如 Linux 的 `epoll`，macOS 的 `kqueue`）非阻塞地监控成千上万个 Socket 的可读写状态。当某个 Socket 缓冲区有数据准备就绪时，事件循环会唤醒对应的协程继续执行，从而在单线程内实现了极高的并发吞吐量。

#### 1.2 `async def` 路由与标准 `def` 路由的底层调度策略差异
在 FastAPI 中，路由函数的定义方式决定了其底层的线程调度机制，开发者对此常有误解：
* **`async def` 路由**：FastAPI 会在主事件循环（Main Event Loop）中直接调用此协程。这就要求在该路由内部**绝对不能出现任何同步阻塞的代码**。例如，如果错误地调用了同步的 `time.sleep(5)` 或是使用了同步的文件读取 `open().read()`，整个事件循环都将被当场锁死，导致此时其他所有用户的并发请求全部卡死挂起。
* **标准 `def` 路由**：FastAPI 内部有一个线程池调度器（基于 `anyio` 的 `ThreadPoolExecutor`）。当遇到声明为标准 `def` 的路由时，FastAPI 会自动将该任务分派给外部线程池中的一个空闲线程去运行。这使得即使在该路由内调用了同步阻塞的读写（如从本地磁盘读 Markdown 文件），也只会在线程池中的独立线程中发生阻塞，而不会破坏主事件循环的运转。

通过线程池执行同步路由虽然保护了主事件循环，但也会带来额外的线程上下文切换开销，并且在高并发下如果线程池占满，后续请求依然需要等待。因此，在条件允许的情况下，尽可能使用异步库并定义为 `async def` 是最优的选择。

**架构设计金律**：
> 如果路由内需要调用第三方同步库（如旧版 `requests`）或执行本地磁盘同步 I/O，请务必使用 `def` 定义路由；如果内部调用的操作均支持异步（如使用 `httpx.AsyncClient` 或是异步读写文件），请使用 `async def`。

#### 1.3 动态路由树与匹配优先级陷阱
FastAPI 底层的路由匹配基于 Starlette 的树形匹配机制。其匹配规则是**自上而下、先声明先匹配**。
当定义了如下路由：
```python
@app.get("/posts/{post_id}")
async def get_post_by_id(post_id: int):
    return {"post_id": post_id}

@app.get("/posts/me")
async def get_current_user_posts():
    return {"data": "current user posts"}
```
当客户端请求 `GET /posts/me` 时，由于 `/posts/{post_id}` 声明在上方，FastAPI 会首先进行匹配。此时它会尝试将字符串 `"me"` 转换为整数 `int`，由于类型转换失败，API 将直接对客户端返回 `422 Unprocessable Entity` 参数验证错误，而排在下方的 `/posts/me` 路由则永远无法被触达。

从底层实现来看，Starlette 的路由器在初始化时，会将所有的路由规则按注册顺序存入一个扁平列表中。在处理请求时，它会依次对列表中的每条规则进行正则匹配测试。一旦命中某条规则，即使后续的数据类型校验失败（如类型强转错误），匹配也会就此终止。因此，静态路由必须始终定义在参数化动态路由的前面。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 1：本地 Markdown 文件解析器

##### 2.1.1 目录结构与准备工作
```text
blog_phase1/
├── main.py
├── posts/
│   ├── 1.md
│   └── 2.md
└── templates/
    └── index.html
```
请在本地创建如上目录，并在 `posts/1.md` 和 `posts/2.md` 中写入简短的 Markdown 原文。

##### 2.1.2 路由架构设计
您需要实现三个核心路由：
1. `GET /`：返回主页的静态页面。
2. `GET /api/v1/posts`：以 JSON 格式返回本地 `posts/` 目录下所有可用的 Markdown 文章 ID 列表。
3. `GET /api/v1/posts/{post_id}`：根据文章 ID 读取并返回该 Markdown 文件的详细纯文本内容。

##### 2.1.3 开发引导流水线
* **第一步：主路径计算与配置**  
  在 `main.py` 中初始化 `FastAPI` 实例。使用 `os.path.dirname(os.path.abspath(__file__))` 锁定当前文件的绝对路径，并派生出 `posts/` 和 `templates/` 目录的绝对路径，避免在多级目录下运行时出现寻址错误。
* **第二步：实现文章列表路由**  
  定义接口 `list_posts`。此步骤需要调用本地同步磁盘读写，因此请考虑：它应该被声明为 `def` 还是 `async def`？使用 `os.listdir` 遍历 `posts/` 目录，将后缀为 `.md` 的文件剥离出 ID，并对其进行排序后以 `{"posts": [...]}` 返回。
* **第三步：实现单篇文章获取路由**  
  定义接口 `get_post`，接收一个路径参数 `post_id: str`。在函数体内拼接出实际的文件绝对路径。
* **第四步：实现首页渲染路由**  
  引入 `fastapi.responses` 中的 `HTMLResponse` 与 `FileResponse`，当用户请求 `/` 时直接返回 `templates/index.html`。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：物理文件缺失兜底**  
  当用户通过 `post_id` 访问文章时，拼装的文件路径可能在物理磁盘上并不存在。在执行 `open` 之前，必须使用 `os.path.exists` 进行前置核验。若文件缺失，必须抛出 `HTTPException(status_code=404, detail="文章不存在")`，绝不能任由程序抛出系统级 `FileNotFoundError` 导致服务产生 500 崩溃。
* **防线二：I/O 阻塞线程冻结**  
  由于本阶段不涉及第三方异步文件操作库（如 `aiofiles`），读取磁盘文件是完全同步的。**请确保将这部分路由定义为普通的 `def`**，以便让 FastAPI 将其安全分派至内部的多线程池中执行。

##### 2.1.5 前端原生 JS 交互与布局蓝图
* **布局设计（极简主义）**：
  * **标题区**：一个大标题 `我的 Markdown 博客`。
  * **列表区**：一个按钮容器（`div`），用于动态挂载文章列表按钮。
  * **正文渲染区**：一个带边框、背景为轻微灰色的 `div`，用于展示文章详情。
* **外部依赖引入**：
  * 在 `<head>` 中通过 CDN 引入 `marked.min.js`，用来将 Markdown 文本实时转化为 HTML：
    ```html
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    ```
* **原生 JavaScript 逻辑控制流程**：
  1. **初始化加载**：页面加载时（`window.onload`），通过原生 `fetch('/api/v1/posts')` 获取所有文章 ID。
  2. **动态生成 DOM**：遍历获取到的 ID 列表，使用 `document.createElement('button')` 动态创建按钮，并将它们挂载到列表容器中。
  3. **事件绑定**：为每个按钮绑定点击事件。当点击按钮时，发起 `fetch('/api/v1/posts/' + id)` 异步请求。
  4. **Markdown 解析与挂载**：获取到后端返回的 `content` 字符串后，调用 `marked.parse(content)` 转换为 HTML，并直接赋值给渲染区的 `innerHTML`。

---

#### 【主线二】事件竞猜与预测市场 - Phase 1：内存竞猜骨架

##### 2.2.1 目录结构与准备工作
```text
prediction_phase1/
├── main.py
└── templates/
    └── index.html
```

##### 2.2.2 路由架构设计
1. `GET /`：返回事件竞猜网关主页。
2. `GET /api/v1/predictions/{event_id}`：获取特定竞猜事件当前的奖池与状态。
3. `POST /api/v1/predictions/{event_id}/bet`：提交下注，接收查询参数 `user_id: str`、`option: str`（如 "yes" 或 "no"）与 `amount: float`。

##### 2.2.3 开发引导流水线
* **第一步：构建内存虚拟数据库**  
  在 `main.py` 顶部使用一个 Python 字典 `PREDICTION_EVENTS` 充当内存数据中心。数据项包含初始事件：
  ```python
  PREDICTION_EVENTS = {
      "tomorrow-rain": {
          "question": "明天会下雨吗？",
          "options": ["yes", "no"],
          "pool": {"yes": 0.0, "no": 0.0},
          "deadline": "2026-12-31 23:59:59",
          "bets_count": 0
      }
  }
  ```
* **第二步：实现查询路由**  
  定义接口 `get_event`。由于该操作仅读取内存字典，属于微秒级 CPU 操作，**请将其声明为 `async def`**，使其直接在主事件循环中完成，无任何额外线程开销。
* **第三步：实现下注路由**  
  定义接口 `place_bet`。接收路径参数 `event_id`，以及查询参数 `user_id`、`option` 和 `amount`。该接口会对指定的竞猜事件选项累加下注金额，并递增下注计数。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：选项合法性校验**  
  在用户提交下注时，必须验证其选择的 `option` 是否属于该事件的合法选项列表（例如：只能是 `"yes"` 或 `"no"`）。如果不满足，必须抛出 `HTTPException(status_code=400, detail="非法的竞猜选项")`。
* **防线二：目标存在性与下注下限校验**  
  若在内存字典中检索不到对应的 `event_id`，必须向客户端反馈 `404` 状态码；同时要限制下注金额 `amount` 必须大于 `0`，否则抛出 `400` 错误。

##### 2.2.5 前端原生 JS 交互与布局蓝图
* **布局设计（极简主义）**：
  * **事件看板**：用加粗标题显示“竞猜问题”（如：明天会下雨吗？）。
  * **状态展示板**：实时展示“Yes 选项总额”和“No 选项总额”，以及“总投注次数”。
  * **交互区**：包含一个“用户ID”文本输入框、一个“下注金额”数字输入框，以及两个分别标注为“押 Yes”和“押 No”的按钮。
* **原生 JavaScript 逻辑控制流程**：
  1. **定时轮询**：定义 `updateEventStatus` 函数，通过 `fetch('/api/v1/predictions/tomorrow-rain')` 周期性（如每隔 2 秒）更新屏幕上的各个选项奖池金额和总下注次数。
  2. **提报下注**：点击“押 Yes”或“押 No”按钮时，提取输入框中的用户ID和下注金额，拼装对应的 URL 查询参数，向 `/api/v1/predictions/tomorrow-rain/bet` 发起 `POST` 请求。
  3. **结果判定**：如果接口返回非 200 状态，提取 JSON 中的 `detail` 错误字段并通过 `alert()` 反馈给用户；若成功则即时调用 `updateEventStatus` 刷新最新数据。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：动态检测新文章
在不重启 FastAPI 服务的情况下，手动在 `posts/` 目录下放置一个全新的 `3.md` 文件。当用户再次访问前端或调用获取列表 API 时，新文章必须能够无缝、动态地显示在列表里。

#### 3.2 技术引导与架构点拨
* 请仔细检查你的 `list_posts` 路由函数。在遍历目录时，是否每一次都是在请求到达时实时执行 `os.listdir` 的？
* **避坑点**：绝对不能在应用程序启动时（全局作用域内）就把文件列表一次性读入内存作为静态列表，否则后续新增的文件将无法被动态感知。

#### 3.3 健壮性防线
* 如果 `posts/` 目录本身在物理磁盘上被意外删除，你的列表接口会崩溃吗？请在此路由中加入前置判断：若该目录不存在，直接返回空列表 `{"posts": []}`，而不是产生 500 崩溃。

---

## 模块二：Pydantic 约束、Markdown 安全上传与元数据解析 (Data & Form)

### 1. 深度补充学习与底层原理解析

#### 2.1 Pydantic V2 核心数据验证图谱
Pydantic V2 是对早期 Python 版本的颠覆性重构，其底层的序列化和验证核心 `pydantic-core` 完全采用 Rust 编写。它的提速原理在于：
1. **编译期图谱构建**：在 Python 进程启动、类加载时，Pydantic 便会在 C 内存空间中编译生成好一张有向验证图谱（Validation Graph）。
2. **零拷贝 coercion（类型强制转换）**：在 Rust 层面直接完成复杂 JSON 的类型强制对齐。例如传入 `"123"` 时，Rust 引擎会在底层自动尝试转型并直接匹配 `int`，无需 Python 解释器在运行时逐级执行昂贵的动态类型查找。

在数据流进入验证图谱时，Pydantic 在 C/Rust 级别直接从字节流构建并过滤值，避免了实例化大量临时 Python 对象产生的 CPU 内存分配开销。此外，Pydantic V2 明确区分了“验证模式”（Validation Mode）与“序列化模式”（Serialization Mode），使得数据在解析输入与输出过滤时，共享同一张在内存中对齐的静态 schema。

#### 2.2 防范 Mass Assignment（批量赋值）漏洞与 DTO 架构设计
在传统框架中，如果直接将 ORM 模型绑定在路由接收端，攻击者可以通过恶意抓包，在提交表单时额外注入如 `"is_admin": true` 或 `"balance": 99999` 等未显式声明的字段。
为了从软件工程层面彻底杜绝此类提权攻击，**DTO（Data Transfer Object，数据传输对象）模式**是业界公认的安全最佳实践：
* **`Input Schema`**：专门用于接收和过滤入参，仅声明允许用户直接修改的字段（如 `title`, `content`），不包含任何权限标识符。
* **`Output Schema`**：用于过滤输出，拦截敏感信息。通过声明 `response_model`，即使数据库查询结果（`ORM Model`）中包含 `password_hash` 等敏感字段，FastAPI 在序列化阶段也会自动将其剥离过滤，杜绝敏感泄露。

在底层，FastAPI 使用 Pydantic 的 `model_validate` 与内置的字段掩蔽机制进行输出转化。当声明了 `response_model` 时，FastAPI 会在运行时构建一个特定的过滤映射图，只提取声明模型中存在的属性进行 JSON 序列化，即使传入的对象包含额外的数据项（Mass Assignment 注入的字段），也会在 Rust 级别的序列化过滤中被直接物理忽略。

#### 2.3 `python-multipart` 数据流式载入机制
当客户端上传文件时（通常通过 `multipart/form-data`），FastAPI 会使用 `python-multipart` 库来解析表单数据。对于上传的文件对象：
* 如果文件大小 **小于 1MB**，为了性能最大化，FastAPI 会将其全部载入系统内存中（`BytesIO`）。
* 一旦文件大小 **超过 1MB**，FastAPI 会自动采用 `SpooledTemporaryFile` 将数据流式分块写入到系统磁盘的临时文件（`/tmp` 目录等）中。这一平滑过渡机制能够彻底防止由于恶意大文件上传导致服务器物理内存爆满（OOM）而崩溃。

在处理大文件流式读取时，底层的 `UploadFile` 提供了一组异步方法（如 `await file.read(chunk_size)`），这些方法由 anyio 异步文件系统接口驱动，确保即使在大块磁盘 I/O 写入时，对应的系统级阻塞调用也会被分配给后台 worker 线程完成，从而保证 FastAPI 事件循环的主线程依然能顺畅处理其他网络数据包。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 2：Markdown 上传与结构化存储

##### 2.1.1 目录结构与准备工作
本模块需要解析多媒体表单，请在命令行中预先装载必需组件：
```bash
pip install python-multipart pydantic
```

##### 2.1.2 路由架构设计
新增高危接口：`POST /api/v1/posts/upload`  
入参要求：
* `file`: 客户端上传的 `.md` 实体文件（采用 `UploadFile` 接收）。
* `author`: 作者名称（通过表单字段 `Form` 接收）。
* `tags`: 标签内容（通过表单字段 `Form` 接收，约定是以逗号分隔的字符串）。

##### 2.1.3 开发引导流水线
* **第一步：建立元数据校验 DTO**  
  在代码中定义 Pydantic Schema 模型 `PostMetadata`。该模型包含 `title: str`、`author: str` 和 `tags: List[str]`。利用 `Field` 限制标题长度在 2 到 100 字符之间。
* **第一步：定义路由及格式核验**  
  定义 `upload_markdown_post` 路由。在入口处，对 `file.filename`进行后缀名核验，只允许 `.md` 文件提交。
* **第三步：安全洗涤与落盘**  
  获取安全处理后的文件名，并在 `posts/` 目录下创建写入句柄。通过 `await file.read()` 异步分块读取文件字节流，并解码保存。
* **第四步：利用 DTO 进行结构化对齐**  
  解析 Form 表单数据，将 `tags` 字符串切片并剔除空白字符，最终传入 `PostMetadata` 进行实例化校验。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：Directory Traversal（目录穿越漏洞）防御**  
  攻击者可能通过构造恶意请求将文件名伪装为 `../../etc/passwd` 或 `../main.py`，企图通过文件上传接口覆盖服务器的关键代码。
  **绝对不能直接拼接原始文件名**！必须使用 `os.path.basename(file.filename)` 截断一切跨路径前缀，确保保存位置被严格限制在 `posts/` 目录下。

##### 2.1.5 前端原生 JS 交互与布局蓝图
* **布局设计**：
  * **文件上传表单（带点线边框）**：
    * 一个文件选择框（`input type="file" accept=".md"`）。
    * 一个文本框用于输入“作者署名”。
    * 一个文本框用于输入“英文逗号隔开的标签（如：FastAPI,Tutorial）”。
    * 一个“开始上传”的绿色按钮。
* **原生 JavaScript 逻辑控制流程**：
  1. **构建 FormData 容器**：点击上传按钮后，在 JS 中实例化一个原生的 `FormData` 对象。
  2. **参数组装**：通过 `formData.append('file', fileInput.files[0])` 将用户选择的文件载入，并附加 `author` 和 `tags` 表单字段。
  3. **发送 multipart 交互**：发起 `fetch` 请求，方法为 `POST`，直接将 `formData` 作为请求体（`body`）发送。**注意**：使用 `FormData` 时，浏览器会自动配置正确的 `Content-Type: multipart/form-data` 及 boundary 分隔符，在原生 `fetch` 中请不要手动指定 `Content-Type` 请求头。

---

#### 【主线二】事件竞猜与预测市场 - Phase 2：下注金额非结构化清洗与格式对齐

##### 2.2.1 目录结构与依赖
本部分完全在内存与类型系统内部完成，不涉及数据库，仅依赖 `pydantic`：
```text
prediction_phase2/
├── main.py
└── templates/
    └── index.html
```

##### 2.2.2 路由架构设计
1. `POST /api/v1/admin/predictions`：管理员创建新的竞猜事件，接收 JSON 请求体。
2. `POST /api/v1/predictions/{event_id}/bet`：用户下注，接收 JSON 请求体（重构第一阶段的 Query 参数接收方式）。

##### 2.2.3 开发引导流水线
* **第一步：建立事件创建 DTO 与正则约束**  
  定义 `EventCreateInput` 模型。
  * `event_id`: 字符串类型，限制长度为 3 至 20 字符。使用 Pydantic 的 `Field(pattern=...)` 约束其只能包含小写英文字母、数字和连字符（如 `"worldcop-2026"`）。
  * `question`: 竞猜问题描述（长度限制为 5 至 100 字符）。
  * `options`: 列表类型 `List[str]`。定义 Pydantic 字段验证器，限制必须包含且仅包含 2 个选项。
  * `deadline_epoch`: 事件封盘截止的 UNIX 时间戳。
* **第二步：建立含有前置清洗器的下注 DTO**  
  定义 `BetInput` 校验类：
  * `user_id`: 投注人 ID（字符串，必填）。
  * `option`: 选择的选项。
  * `raw_amount`: 用户提交的原始文本金额（类型为 `str`，例如 `"￥1500"`、`"200 coins"` 或 `"$100"`）。
* **第三步：实现 Pre-validator 清洗逻辑**  
  在 `BetInput` 中使用 Pydantic 的 `@field_validator("raw_amount", mode="before")` 声明前置验证器。
  * 在校验函数内部，使用 `re` 正则表达式匹配文本。提取第一个包含小数或整数的连续数字串，并转换为浮点数。
  * 将清洗后转换出来的数值返回给 Pydantic 做后续的类型对齐。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：非法输入清洗异常拦截**  
  如果用户故意输入不含任何数字的非结构化垃圾字符（如 `"五百金币"`），正则匹配将会失败。此时校验器必须显式抛出 `ValueError("未能识别出有效的下注金额数字")` 告知 Pydantic。Pydantic 会捕获该错误并优雅地为客户端呈现 `422 Unprocessable Entity` 的结构化错误详情。

##### 2.2.5 前端原生 JS 交互与布局蓝图
* **布局设计**：
  * **创建竞猜事件表单**：提供“事件ID（正则约束）”、“竞猜问题”、“选项一”、“选项二”、“截止时间戳”的文本输入框以及“一键创建”按钮。
  * **非结构化下注区**：出价输入框改为文本输入框（`input type="text"`），允许用户输入任何携带货币单位的混杂格式字符（如 `$1800`）。
* **原生 JavaScript 逻辑控制流程**：
  1. **提交创建事件**：提取创建表单中的值，组装为 JSON 并指定 `'Content-Type': 'application/json'` 后发送 `POST` 请求至 `/api/v1/admin/predictions`。
  2. **提报非结构化投注**：提取输入框中的原始字符串值。组装成 JSON 数据：`JSON.stringify({ user_id: "user_01", option: "yes", raw_amount: rawInput })` 发送至下注接口。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：限制上传文件的大小
在 `/api/v1/posts/upload` 接口中建立安全防火墙，如果用户上传的文件总字节大小超过了 `100KB`，则拒绝写入本地磁盘，并立即向客户端返回 `400 Bad Request` 状态码。

#### 3.2 技术引导与架构点拨
* 当你在接口中挂载 `file: UploadFile` 时，FastAPI 会自动将其封装。该对象持有一个底层的 Python 临时文件句柄。
* 我们可以通过 `file.size`（如果 FastAPI 版本支持）或者通过 `await file.read()` 获取内容后计算 `len(content_bytes)` 来检测字节长度。
* **避坑点**：请注意，如果使用 `await file.read()` 读取了全部内容，文件读取指针会被移动到末尾。如果你接下来还要将其写入文件，必须先调用 `await file.seek(0)` 重置指针位置，否则写入磁盘的文件会是空白的。

#### 3.3 健壮性防线
* 必须在将内容写入磁盘文件系统**之前**拦截并检查大小，防止由于超大恶意文件写入直接塞满服务器磁盘空间。

---

## 模块三：依赖注入的应用——读者 XP 追踪器与防刷限流 (Dependencies)

### 1. 深度补充学习与底层原理解析

#### 3.1 依赖关系的有向无环图 (DAG) 解析算法
在应用初始化以及路由加载期间，FastAPI 引擎会递归解析路由函数签名，并为每个路由生成一张**有向无环图 (Directed Acyclic Graph, DAG)**。
例如，若路由声明依赖了 `db: Session = Depends(get_db)` 与 `user: User = Depends(get_current_user)`，而 `get_current_user` 本身又声明依赖了 `db: Session = Depends(get_db)`。
1. FastAPI 会在拓扑排序解析中发现：`get_current_user` 和路由都依赖于同一个 `get_db` 产生器。
2. 当 `use_cache=True` 时，FastAPI 在单个请求生命周期内**仅会调用一次 `get_db`**，并将其产生值缓存。随后，当 `get_current_user` 和路由请求获取 `db` 时，将直接共用该缓存在内存中的同一 Session。这不仅减少了大量重复计算，而且避免了单个请求中由于多次初始化数据库 Session 引起的连接爆满以及数据库事务边界隔离错乱问题。

FastAPI 的依赖注入系统在路由加载时通过 `inspect` 库扫描路由函数的签名，构建内部的 `Dependant` 对象树。在运行时，它使用一个拓扑排序算法来解析这一依赖关系 DAG。当 `use_cache=True` 时，解析器会维护一个以依赖项函数引用（Callable）作为 Key 的临时缓存映射字典，这就保障了多层嵌套深度子依赖在同一个 HTTP 请求的上下文中绝对不会被重复实例化和执行。

#### 3.2 异步生成器（Generator Dependency）生命周期边界与 `yield` 底层原理
使用 `yield` 声明的依赖项本质上是一个 Python 的 Context Manager（上下文管理器）：
```python
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db  # <--- 控制权交接分界线
    finally:
        await db.close()  # <--- 逆向折返扫尾区
```
* **生命周期跨越**：当请求到达时，FastAPI 运行依赖并直到 `yield` 语句处执行挂起，并将 `db` 对象注入路由。随后路由函数开始执行。
* **逆向折返扫尾**：无论路由函数执行是正常结束，还是由于抛出异常导致非正常退出崩溃，FastAPI 底层基于 ASGI 生命周期拦截机制，都必定重新将控制权交回给依赖函数，强制执行 `finally` 块中的扫尾代码。这确保了如数据库 Session、Redis 连接池、临时物理文件句柄等资源的可靠释放。

在幕后，FastAPI 使用内置的 `contextlib.asynccontextmanager` 对包含 `yield` 的依赖函数进行包装。当网络响应发送完毕、或者路由执行期间发生异常报错时，Starlette 的 HTTP 连接管理中间件会介入，并驱动 Python 协程生成器抛出并传递对应的异常到生成器的挂起帧。这强制激活了生成器的 `finally` 清理语句，确保了资源无论在何种边界状况下都不会泄露。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 3：读者经验等级 (XP) 计算器

##### 2.1.1 目录结构与准备工作
```text
blog_phase3/
├── app/
│   ├── __init__.py
│   └── dependencies.py
├── main.py
└── templates/
    └── index.html
```

##### 2.1.2 路由架构设计
1. 新增安全受控阅读路由：`GET /api/v1/posts/{post_id}/read-secured`
2. 读者标识注入：在进入路由前，必须在请求头中携带一个识别身份的 Header：`X-Reader-Id`。
3. 动态响应更新：路由处理完后，需要将当前读者的“升级后等级”与“总 XP 经验”注入到 Response 响应头（`X-Reader-Level`, `X-Reader-XP`）中返回。

##### 2.1.3 开发引导流水线
* **第一步：建立内存持久字典**  
  在 `dependencies.py` 中初始化一个全局字典 `VISITOR_XP_DATABASE`，用来存储不同读者的累计经验值。
* **第二步：设计类依赖项（Class Dependency）**  
  设计类 `ExpTrackerDependency`。在 `__init__` 构造器中接收一个默认步长 `xp_step: int = 10`。
* **第三步：编写 Callable 调用逻辑**  
  在类中实现 `async def __call__(self, request: Request, response: Response, x_reader_id: str = Header("Guest-Reader"))`。
  * 从请求头中解析出 `x_reader_id`。
  * 将其在 `VISITOR_XP_DATABASE` 中对应的值累加 `xp_step` 经验。
  * **利用 `yield` 将控制权交还给路由**。
  * **在 `yield` 执行完毕后的后续流程里**，利用数学公式换算出用户的等级（例如每 30 点经验升一级）。
  * 将升级数据写入 `response.headers["X-Reader-Level"]`。
* **第四步：在主路由上装载实例**  
  在 `main.py` 中实例化该类：`reader_xp_tracker = ExpTrackerDependency(xp_step=15)`。在业务路由中使用 `active_reader: str = Depends(reader_xp_tracker)` 挂载此依赖项。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：空请求头优雅降级**  
  声明 `x_reader_id: str = Header("Guest-Reader")`。FastAPI 会自动尝试提取 `X-Reader-Id` 头部（自动转换横杠与下划线）。若客户端未传递，则优雅地降级回退至 `"Guest-Reader"`，保证接口不报错崩溃。

##### 2.1.5 前端原生 JS 交互与布局蓝图
* **布局设计**：
  * **读者徽章显示牌**：显示“当前读者账号”与“读者当前等级/经验”。
  * **阅读按钮**：点击触发对受控文章的读取，并随之赚取经验。
* **原生 JavaScript 逻辑控制流程**：
  1. 设定请求头：在 fetch 的配置项 `headers` 中写入 `'X-Reader-Id': 'Reader_My_ID'`。
  2. 获取响应头：fetch 请求成功后，不仅要读取 `res.json()` 的返回体，还要通过 `res.headers.get('X-Reader-Level')` 取出后端在 `yield` 后置链路中返回的等级指标，并将其渲染到前端徽章卡板中。

---

#### 【主线二】事件竞猜与预测市场 - Phase 3：下注接口 IP 频率限制依赖

##### 2.2.1 目录结构与依赖
本功能仅在依赖层级完成，在 `app/dependencies/limiter.py` 中编写限流规则：
```text
prediction_phase3/
├── app/
│   ├── __init__.py
│   └── dependencies.py
├── main.py
└── templates/
    └── index.html
```

##### 2.2.2 路由架构设计
将前述的 `POST /api/v1/predictions/{event_id}/bet` 接口纳入安全频限保护范围。任何调用此下注接口的用户，必须通过时间窗口核验。

##### 2.2.3 开发引导流水线
* **第一步：内存时间戳存储初始化**  
  在 `dependencies.py` 中初始化全局字典 `IP_TIMESTAMPS`，结构为：`{ "IP地址": [时间戳1, 时间戳2, ...] }`。
* **第二步：实现滑动窗口类**  
  编写类 `SlidewindowRateLimiter`。构造器中接收两个初始化参数：`max_requests: int`（允许的最大请求次数）与 `window_seconds: int`（滑动窗口时长）。
* **第三步：动态洗涤与核查**  
  在类中实现 `async def __call__(self, request: Request)` 逻辑使其成为可调用的依赖项：
  * 通过 `request.client.host` 抓取客户端的网络 IP。
  * 获取当前的时间戳 `now = time.time()`。
  * 提取并清洗该 IP 对应的历史时间戳队列：剔除所有超过当前滑动窗口周期（`now - window_seconds`）的旧时间戳。
  * 判断残留队列的长度。如果长度达到或超过了 `max_requests`，则直接阻断；若未超限，则将最新的 `now` 时间戳追加进队列，放行请求。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：超频主动封禁异常与内存释放**  
  在验证超频时，必须抛出 `HTTPException(status_code=429, detail="下注太频繁，请稍后再试")`。由于在依赖项中抛出的异常会被 FastAPI 的全局异常处理器统一捕获，这将立刻阻断后续业务下注逻辑。同时，每次请求到达时都要执行剔除过期时间戳的操作，防止由于高频历史时间戳无限积压导致物理内存耗尽。

##### 2.2.5 前端原生 JS 交互与布局蓝图
* **布局设计**：
  * 在页面中央显式提供一个下注提示框。
* **原生 JavaScript 逻辑控制流程**：
  * 用户连续点击“押注”按钮提交请求。如果 fetch 请求返回的状态码是 `429`，则在界面弹窗展示 `detail` 返回的“下注太频繁”警告，且让下注按钮置灰禁用 3 秒。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：全局系统性能监控依赖
利用 `yield` 的两阶段运行机制，设计并实现一个极简的系统性能时间监控依赖器。它能够记录并打印每一个接口从“接收请求”到“最终发送响应”所耗费的精确物理时间。

#### 3.2 技术引导与架构点拨
* 编写一个异步依赖项函数。在 `yield` 之前通过 `time.perf_counter()` 锁定启动时间。
* 执行 `yield` 将控制权让渡出去。
* **在 `yield` 的下一行**，再次读取当前时间，并求差值，通过 `print()` 或 `logging` 控制台输出。

#### 3.3 健壮性防线
* 确保在整个依赖块中使用 `try...finally` 包裹 `yield`。
* **避坑点**：如果接口路由处理发生异常报错（如 404、500），缺少 `finally` 的 `yield` 将可能导致后置统计代码被直接跳过，而无法记录接口运行时间。

---

## 模块四：安全保护——博主后台 JWT 认证与防篡改数字签名 (Security & JWT)

### 1. 深度补充学习与底层原理解析

#### 4.1 JWT 令牌结构与非对称签名 (RS256) 架构剖析
JSON Web Token (JWT) 是由 `Header` (头部)、`Payload` (载荷)、`Signature` (签名) 三个部分通过英文半角句号 `.` 连接而成的字符串。
* **对称加密签名 (HS256)**：签发和验证时使用同一把 `SECRET_KEY`。一旦微服务节点增多，必须共享该密钥进行身份验证。只要有一个节点被攻破泄露密钥，全局系统将丧失信任防线。
* **非对称加密签名 (RS256)**：授权服务器持有高防密级的**私钥（Private Key）**专门负责签发，而外部业务网关或第三方微服务只分发持有**公钥（Public Key）**用来验签。公钥即使被攻击者窃取，由于单向陷门函数的不可逆性，他也绝对无法逆向仿冒签发令牌。这极大地收敛了高危写操作的攻击面。

非对称加密算法（如 RS256）的核心数学原理基于大整数素因子分解的困难性。私钥用于进行私密性的数学指数运算生成签名，公钥则在轻量级乘法逆元运算下快速对签名进行解密核算。这一分工使得微服务集群（甚至前端）可以在只暴露公钥的情况下对 Token 执行本地化校验，完美切断了主密钥在不安全通信链条上被嗅探窃取的可能性。

#### 4.2 双令牌 (Access & Refresh) 交互生命周期演进
在严格的软件工程中，单一的 Token 往往面临“寿命太长不安全”与“寿命太短影响体验”的双重矛盾。**双令牌架构**解决了这一痛点：
1. **Access Token（访问令牌）**：生命周期通常设为 15 分钟，权限完整。每次请求业务接口时在 Header 中传递，由于高频曝光，需维持短寿命。
2. **Refresh Token（刷新令牌）**：生命周期通常设为 7 天，常驻在 `HttpOnly Cookie` 中（阻止 JavaScript 跨站脚本读取，免疫 XSS 攻击），权限极其单一，仅限于用来向 `/auth/refresh` 接口兑换一个新的 Access Token，避免了由于 Access Token 过期导致用户频繁被踢下线、需要反复重新输入密码的尴尬体验。

在防御策略上，Refresh Token 通常配合“一次性重放检测机制”（Token Rotation）运行。当服务器收到 `/auth/refresh` 提报请求时，会自动作废当前提交的旧 Refresh Token 并下发一对崭新的 Access / Refresh 组合。一旦黑客使用过期的或被盗窃的旧 Refresh Token 尝试发起二次兑换请求，系统安全风控中心能立即触发机制并强制将当前用户的全局会话全部阻断拉黑，保障资产安全。

#### 4.3 密码学的防线：时序攻击 (Timing Attack) 与 `compare_digest`
在身份验证中，比对两个密匙签名如果采用传统的 `==` 运算符，判定机制通常是：从左到右逐个字符比对，只要发现某位不一致就立刻中断返回 `False`。
黑客可以通过部署微秒级 high-precision 物理计时器，根据服务器对不同签名的响应返回耗时，推断出其在前几位字符的比对进度，从而逐步刺探出正确的数字签章。这就是经典的**时序攻击（Timing Attack）**。

`hmac.compare_digest(a, b)` 则是通过底层 C 代码实现的一种**常数时间比对算法 (Constant-Time Algorithm)**。无论在前几位匹配上，它都强制完整扫描并比对完所有的二进制位，不给黑客留下基于网络请求延时的分析余地。

传统的字符串按位比较算法具有“短路校验”特征。而在密码学世界，哪怕是在第 16 位字符不匹配，也必须保证运行完与在第 1 位不匹配时完全相等的 CPU 时钟周期。`compare_digest` 通过对两个输入数组执行逐位异或（XOR）运算并对运算结果执行累加，直到最后一步才判定累加值是否为零。这彻底消除了网络耗时上的微小方差，物理锁死了基于延时波动的旁路攻击通道。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 4：博主管理后台 JWT 拦截壁垒

##### 2.1.1 目录结构与准备工作
```text
blog_phase4/
├── main.py
└── templates/
    ├── index.html
    └── login.html
```
请在命令行中拉取专业加解密套件：
```bash
pip install python-jose[cryptography] python-multipart
```

##### 2.1.2 路由架构设计
1. `GET /login`：返回博主登录页面。
2. `POST /api/v1/auth/login`：用户凭证核验，若成功则发放 JWT Token。
3. `POST /api/v1/posts/secured-publish`：管理员安全发布接口。

##### 2.1.3 开发引导流水线
* **第一步：建立认证底座**  
  在 `main.py` 顶部引入 `fastapi.security` 模块中的 `OAuth2PasswordBearer`。它会自动帮助拦截 HTTP Request Headers 里的 `Authorization: Bearer <Token>`。
* **第二步：编写 JWT 生产机器**  
  使用 `jose.jwt` 构建 `create_access_token` 生成器。包含 `sub`（主体声明，如用户名）与 `exp`（过期截止时间）。
* **第三步：构建管理员鉴权依赖函数**  
  编写 `get_current_admin` 函数，作为路由依赖项挂载。
  * 该函数接收自动解析出来的 Bearer Token。
  * 调用 `jwt.decode` 解密。
  * 判断 payload 载荷中的 `role` 角色标识是否为 `"admin"`。
* **第四步：给发布路由上锁**  
  在 `secured-publish` 路由函数中声明入参 `admin_user = Depends(get_current_admin)`。不满足权限要求的请求将被挡在路由门外。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：密码比对与加密解密崩溃兜底**  
  在解码 JWT Token 时，如果 Token 遭到篡改、伪造、或者时间已经过期，`jwt.decode` 会直接抛出 `JWTError` 异常。请务必使用 `try...except JWTError` 捕获所有解码异常，并抛出 `401 Unauthorized` 状态码，千万不能让此类外部异常暴露导致服务内部崩溃。

##### 2.1.5 前端原生 JS 交互与布局蓝图
* **布局设计（两阶段多页面）**：
  * **登录页（login.html）**：输入账号 `admin` 与密码，并附有“登录”按钮。
  * **撰写页（index.html）**：提供标题、正文文本输入域，并有一个“发布博文”按钮。
* **原生 JavaScript 逻辑控制流程**：
  1. **登录并存储凭证**：在登录页面输入账号密码。fetch 发起 POST 提交（推荐使用 `URLSearchParams` 或 FormData 格式契合 `OAuth2PasswordRequestForm`）。
  2. **本地落盘**：核验通过后，服务器会回传 `access_token`。在 JS 中执行 `localStorage.setItem("authToken", data.access_token)` 暂存本地。
  3. **受控资源携带访问**：在撰写页面，当点击“发布博文”时，先通过 `localStorage.getItem("authToken")` 取出 Token。在 fetch 的 headers 中，手动拼装并携带 `'Authorization': 'Bearer ' + token` 头部。

---

#### 【主线二】事件竞猜与预测市场 - Phase 4：安全结算与结果提报防篡改签名机制

##### 2.2.1 目录结构与核心依赖
本功能不需要数据库支持，只需 Python 的标准库 `hmac` 和 `hashlib`：
```text
prediction_phase4/
├── main.py
└── templates/
    └── index.html
```

##### 2.2.2 路由架构设计
1. `POST /api/v1/admin/predictions/{event_id}/settle`：管理员结算竞猜事件。
由于本阶段我们还没有建立复杂的数据库管理员账户，为了防止恶意调用，我们在该高危结算接口上部署基于 **HMAC 共享密钥的防篡改数字签名验证**。
客户端发起结果提报结算时，除了传递判定正确的选项外，必须在 Header 额外提供：
* `X-Signature`: 验签哈希值
* `X-Timestamp`: 签名生成时的时间戳（用来防重放攻击）

##### 2.2.3 开发引导流水线
* **第一步：共享密钥配置**  
  在服务端配置文件中，设定一套不公开的共享密匙：`ORACLE_SHARED_SECRET = "ADMIN_SECURE_KEY"`。
* **第一步：编写 Hmac 签名验证依赖项**  
  编写依赖项函数 `verify_oracle_signature`。
  * 提取请求头中的 `X-Signature`、`X-Timestamp` 以及查询参数或请求体中的结果数据。
  * 校验时差防篡改重放：用当前的时间减去 `X-Timestamp`。如果时差超过 300 秒（5 分钟），立即判定该签名请求为非法的网络重放篡改，拒绝执行。
  * 构建签名体文本：将 `X-Timestamp` 字符串、`event_id` 以及正确选项 `winning_option` 拼接起来。
  * 用共享密钥结合 `hashlib.sha256` 算法，在后端重新进行哈希计算：`hmac.new(key, msg, sha256).hexdigest()`。
* **第三步：拦截注入与比对**  
  在 `settle` 路由中，挂载该依赖：`Depends(verify_oracle_signature)`。比对接收到的签名与本地计算出的签名是否完全对齐。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：时序攻击物理阻断**  
  在校验本地计算生成的 HMAC 和客户端上传的 `X-Signature` 是否相等时，**严禁直接使用 Python 的 `==` 运算符**！必须使用 `hmac.compare_digest` 从而消除时序侧信道攻击风险。

##### 2.2.5 前端原生 JS 交互与布局蓝图
* **布局设计**：
  * 提供一个简单的事件结算工具栏：下拉选择哪一个选项为“正确答案”，一个按钮“确认结算”。
* **原生 JavaScript 逻辑控制流程**：
  * 在安全结算或集成测试脚本中，原生 JS 获取当前的 Unix 时间戳。
  * 利用本地密钥在签名端算法中算出哈希串（或通过安全工具算好）。
  * 在向 `/api/v1/admin/predictions/{event_id}/settle` 接口提报时，将生成的哈希串写入 `headers: { 'X-Signature': signature, 'X-Timestamp': timestamp }` 并提报。若验证通过，事件进入结算成功，冻结金额清算放行。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：新增客户端 JWT 注销清空机制
在博客前端主页增设“退出登录”按钮。点击该按钮后，客户端能够主动清空身份凭证，并在后续对受控发布资源访问时被服务器拦截阻断。

#### 3.2 技术引导与架构点拨
* 这是对纯前端会话管理的训练。在“退出登录”按钮的点击事件中，调用 `localStorage.removeItem("authToken")` 剔除缓存在本地的 JWT 字符串，随后刷新当前页面。
* 刷新页面后，再次点击“发布博文”，系统会由于缺失 `Authorization` 请求头而自动拒绝本次提报，并在界面提示需要重新登录。

#### 3.3 健壮性防线
* 前端应做好兜底判断：读取 localStorage 前，如果 `token` 变量未定义或为空，应该直接在前端进行提示阻断（比如让发布按钮变为禁用置灰状态），避免发起无效的 HTTP 请求。

---

## 模块五：数据库实战与异步并发风暴 (Databases & Async ORM)

### 1. 深度补充学习与底层原理解析

#### 5.1 SQLAlchemy 2.0 异步运行时的执行机制差异
在 SQLAlchemy 1.x 时代，由于依赖隐式、惰性的关系加载（Lazy Loading），许多数据库读写是在对象属性被访问时自动、同步发生的，这极大阻碍了异步框架的发展。
**SQLAlchemy 2.0 彻底取消了隐式的同步会话，转向显式执行流模型**。
* **统一执行范式**：不再使用 `session.query(User).filter(...)`，改为声明式 `select(User).where(...)` 构建静态 AST，再使用 `session.execute(statement)` 显式发起驱动层面的非阻塞底层协程交互 [5.1]。
* **本地 `aiosqlite` 的特殊机制**：SQLite 数据库本身是一个物理文件系统，并没有独立非阻塞的套接字（Socket）通信层。因此，其异步驱动 `aiosqlite` 在底层并不是真正的网络 I/O 轮询，而是**利用了后台进程组/轻量线程组专门跑同步写锁，用主事件循环驱动来欺骗上游解释器**。这一架构在本地开发环境中可实现零物理环境开销的高仿异步体验，而一旦在生产环境上多节点运行时，需平滑修改 `DATABASE_URL` 切换为真正的生产级异步数据库驱动 `asyncpg` (PostgreSQL)。

在异步架构中，SQLAlchemy 2.0 强制引入了 `AsyncSession` 的概念，并通过 greenlet 机制来模拟支持某些遗留的上下文。在使用真正的异步数据库驱动（例如用于 PostgreSQL 的 `asyncpg`）时，SQLAlchemy 会构建非阻塞的长 Socket 连接，所有的 SQL 查询发送和结果数据接收都通过底层的 `asyncio.Protocol` 进行，在等待数据库返回时会将事件循环的 CPU 控制权安全让渡给其他路由请求。

#### 5.2 并发致命坑洞：1 对多、多对多关联下的 N+1 慢查询原理解析
当读取了 A 表中的 $N$ 条记录，而每条记录关联了 B 表。在循环读取时如果直接使用 A 记录去查其关联属性 B，数据库默认的 `lazy='select'` 机制会发起 $1$ 次查询拉取 A，再紧接发起 $N$ 次**独立的、阻塞性的 SQL 语句**拉取对应的 B：
```sql
-- 第 1 次主查询
SELECT * FROM blog_posts;
-- 紧接着由 Python 解释器在循环内发出 N 次子查询
SELECT * FROM tags WHERE post_id = 1;
SELECT * FROM tags WHERE post_id = 2;
...
```
在海量并发的 Web 系统中，N+1 问题会导致物理连接池被瞬间打满，接口响应时间在并发增大时呈指数级恶化。

**SQLAlchemy 2.0 提供的终极性能解毒手段**：
*   **`joinedload` (联表急切加载)**：直接构建带有 `LEFT OUTER JOIN` 的大 SQL，一次性将关联的多张表内容整体拉回。适用于多对一 (Many-to-One) 或一对一关联 [5.2]。
*   **`selectinload` (集合急切加载)**：首先查询 A 表；拿到 A 表所有的 ID 后，自动构造一个聚合后的 `IN` 查询，一并把关联内容取回：
```sql
SELECT * FROM blog_posts;
-- 仅通过第 2 次聚合查询将关联字段一次性批量揽收
SELECT * FROM tags WHERE post_id IN (1, 2, 3, 4, 5...);
```
适用于一对多 (One-to-Many) 或多对多 (Many-to-Many) 的复杂关系，能够极大提升高并发条件下的数据库查询吞吐量 [5.2]。

在关系数据库解析中，`joinedload` 的主要开销在于其返回的笛卡尔积。如果子表数据极其庞大，网络传输冗余重复字段的开销将吞噬掉省下的网络往返时间。而 `selectinload` 的巧妙之处在于将两次查询完全独立，第一阶段在内存中完成主记录 ID 的合并，第二阶段通过一个 `IN` 操作极速捕获子表记录。这种方式最大程度减轻了数据库内部联表查询的 CPU 锁争用。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 5：SQLite 异步驱动接入

##### 2.1.1 目录结构与准备工作
```text
blog_phase5/
├── app/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── main.py
└── templates/
    └── index.html
```
引入 ORM 操作底层套件：
```bash
pip install sqlalchemy aiosqlite
```

##### 2.1.2 路由架构设计
1. 开机启动钩子：在程序启动时自动检测并建好表文件结构。
2. `POST /api/v1/posts/db-add`：异步将博文实体持久化保存入 SQLite 数据库。
3. `GET /api/v1/posts/db-all`：异步从数据库读出所有发布的博文信息。

##### 2.1.3 开发引导流水线
* **第一步：建立实体映射（Models）**  
  在 `models.py` 中，定义基类 `Base(DeclarativeBase)`。构建映射类 `DBBlogPost(Base)`。使用 2.0 显式强类型语法 `Mapped` 定义主键 `id`、`title`、`content` 等属性。
* **第二步：配置异步会话池**  
  在 `db.py` 中，构建异步连接引擎 `create_async_engine("sqlite+aiosqlite:///./test_blog.db")`。利用 `async_sessionmaker` 配置会话容器。
* **第三步：编写依赖生成工厂**  
  编写异步 `get_db_session()` 生成器函数，利用 `yield` 提供 `session`。
* **第四步：实现业务落盘路由**  
  在 `main.py` 的路由中注入 `db: AsyncSession = Depends(get_db_session)`。使用统一执行范式（如 `db.add`、`await db.commit()`）来完成对数据的增、查等操作。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：异步提交资源泄露防范**  
  在异步数据库读写时，**必须确保所有写操作在提交失败时能够自动回滚（Rollback）**。
  在业务层或依赖层级使用上下文管理器（如 `async with session:`）能确保会话即使在请求途中因为其他意外断网挂掉，也会在 `finally` 折返逻辑中安全释放对 SQLite 数据库的占用锁。

##### 2.1.5 前端 Vue 3 交互与布局蓝图（正式平滑迁移至 Vue 3）
* *提示：由于数据库操作逻辑数据链条增多，本模块起前端交互框架升级为极简 Vue 3 CDN。我们不再编写庞大无序的原生 DOM 拼接，而是采用响应式数据模型驱动。*
* **布局设计**：
  * 两栏布局：
    * **左侧：新增博文面板**（输入标题、Markdown 内容的文本域，以及一键保存入库按钮）。
    * **右侧：数据库拉取展台**（列出数据库里的文章，标注物理 ID 以及入库时间）。
* **外部依赖引入**：
  ```html
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  ```
* **Vue 3 核心状态与行为驱动逻辑（不提供完整代码，提供逻辑链）**：
  1. **状态驱动区**：在 `setup()` 中声明响应式变量（`ref`）: `posts` (文章列表数组)、`title`、`content`。
  2. **行为钩子区**：定义 `loadDatabasePosts` 异步加载方法，执行 `fetch('/api/v1/posts/db-all')`，获取成功后直接更新 `posts.value` 数组，Vue 会自动在界面刷新 DOM。
  3. **生命周期挂载**：在 `onMounted()` 时自动调用初始化加载。
  4. **提交表单**：定义 `saveToDatabase` 方法，通过 `URLSearchParams` 将 `title` 和 `content` 的双向绑定变量内容传输给 `/api/v1/posts/db-add` 接口，提交成功后直接触发调用 `loadDatabasePosts()` 实现即时自刷。

---

#### 【主线二】事件竞猜与预测市场 - Phase 5：高并发下防超额下注与资金安全独占锁 (`with_for_update`)

##### 2.2.1 目录结构与模型依赖
```text
prediction_phase5/
├── app/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── main.py
└── templates/
    └── index.html
```

##### 2.2.2 路由架构设计
1. 开机自动生成 SQLite 数据库及数据表文件。
2. `POST /api/v1/predictions/db-bet`：数据库版异步下注接口。
当高并发用户同时点击下注时，为了避免“并发超支”（即用户原本只有 100 虚拟币，却在毫秒级并发下发出了两个 100 币的下注请求，由于查询间隔导致两次判定均通过），必须加锁保护资金。

##### 2.2.3 开发引导流水线
* **第一步：建立数据库实体映射模型**  
  在 `models.py` 中使用 SQLAlchemy 2.0 声明模型：
  * `DBUser` 表：包含 `id`、`balance`（可用余额，浮点数）、`frozen_balance`（冻结余额，浮点数）。
  * `DBPredictionEvent` 表：包含 `id`、`question`、`options`、`is_settled`（布尔值）、`winning_option`。
  * `DBBet` 表：包含 `id`、`user_id`、`event_id`、`option`、`amount`。
* **第二步：编写锁定读选语句与独占事务边界**  
  在 `db-bet` 路由中，获取数据库连接 `AsyncSession`。
  * 使用 `async with db.begin():` 显式开启数据库隔离事务块。
  * 在执行扣减用户虚拟币之前，通过 `.with_for_update()` 构筑排他性读锁（行级悲观锁），查询扣除余额的用户：
    ```python
    stmt = select(DBUser).where(DBUser.id == user_id).with_for_update()
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    ```
* **第三步：串行判定与状态变更**  
  * 数据库底层锁定此用户行。此时其他同时到达的该用户下注线程只能在此排队等候。
  * 安全核对锁定的行数据：如果 `user.balance < bet_amount`，直接抛出 `HTTPException(400, "可用余额不足")`。由于在 `db.begin()` 内抛出异常，本次事务将安全回滚（Rollback）。
  * 若余额充足：将金额从 `balance` 中扣除并追加至 `frozen_balance`，插入下注历史记录，提交事务。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：悲观行级锁死锁防御**  
  在高并发多并发模型中，行级锁 `with_for_update` 如果加锁顺序混乱，会造成死锁。
  **避坑点**：确保整个系统加锁流程中的事务获取规则完全是一致的串行化单链结构。始终严格遵守先锁 `DBUser` 用户行，完成虚拟币扣留后，再写入/修改 `DBBet` 或 `DBPredictionEvent`。切勿发生“有的接口先锁事件，再锁用户；有的接口先锁用户，再锁事件”的交叉逆向加锁乱序。

##### 2.2.5 前端 Vue 3 交互与布局蓝图
* **布局设计**：
  * **用户资产中心**：展示当前测试用户 ID、可用金币余额（`balance`）、冻结中金币（`frozen_balance`）。
  * **竞猜交互板块**：包含下注选项和投注输入框、下注按钮。
* **Vue 3 核心状态与行为驱动逻辑**：
  1. **响应状态绑定**：使用 `ref` 双向绑定金币。
  2. **高频防抖逻辑**：点击下注按钮触发 `POST`。后端若在悲观事务流中返回“余额不足”，立刻反馈并将用户账户余额强制校准对齐。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：新增数据库删除功能
在博文系统主干中实现物理擦除功能，提供 `DELETE /api/v1/posts/db-delete/{post_id}` 接口。当用户在前端点击对应文章后侧的“物理销毁”按钮时，该条文章能安全地被从 SQLite 数据库中异步移除，并刷新当前列表展示。

#### 3.2 技术引导与架构点拨
* 引入 SQLAlchemy 的 `delete` 构建表达式：`delete(DBBlogPost).where(DBBlogPost.id == post_id)`。
* 使用 `db.execute()` 执行此擦除命令。
* **避坑点**：记得最后必须加上 `await db.commit()`。如果没有调用 commit，该物理事务将不会在磁盘上发生修改，数据将在会话结束后被隐式自动回滚。

#### 3.3 健壮性防线
* 如果传入的 `post_id` 在底层查无此记录，执行 `delete` 后并不会抛错，但建议进行前置验证：首先查一次确认该 ID 的实体确实存在；若不存在，抛出 `404 Not Found` 错误，避免无效数据库事务浪费。

---

## 模块六：实时并发——WebSocket 弹幕大屏与生产部署 (WebSockets & Deploy)

### 1. 深度补充学习与底层原理解析

#### 6.1 WebSocket 101 Connection Upgrade 握手断连底层原理解析
传统的 HTTP 协议是单向的，只有客户端能发起请求。**WebSocket 则是建立在 TCP 基础上的双向全双工对等网络协议**。
1. **握手升级 (Handshake Upgrade)**：客户端首先发起一个标准的 HTTP 请求，并在 Header 中声明：
   ```http
   Upgrade: websocket
   Connection: Upgrade
   ```
2. **协议变更**：FastAPI 底层的 Starlette 拦截到后，如果同意升级，则向客户端回传 `HTTP/1.1 101 Switching Protocols`。
3. **TCP 持久连接**：此时原先的 HTTP 连接正式转变为 WebSocket 长连接通道。双方可以在任何时候向对方主动推送二进制或文本流，免去了反复重连及昂贵的 HTTP 报文头带宽损耗。
4. **断连容错机制**：由于网络物理波动，客户端可能在毫无感知的情况下与服务器失去连接。此时如果服务器继续调用 `websocket.send()` 将抛出严重的管道写错误（Broken Pipe / Connection Closed）。因此，后端在运行时必须将其放入 `try-except WebSocketDisconnect` 结构块中，保证对掉线僵尸连接的自动剔除，保障内存容量不发生物理泄露。

根据 RFC 6455 协议规范，WebSocket 握手的核心防伪机制是客户端随机生成的 `Sec-WebSocket-Key`。服务端在收到此 Key 后，会将它与全局固定的 GUID 常量拼接，进行 SHA-1 签名哈希，并进行 Base64 编码，最终以 `Sec-WebSocket-Accept` 返回客户端以确认握手。长连接一旦形成，数据便被包裹在特定的小型“帧”（Frame）中传输。客户端帧必须通过特定算法做异或掩码（Mask）混淆，而服务端向客户端发送的帧则不需要，这种不对称设计可有效防御传统 HTTP 代理网络缓存污染漏洞。

#### 6.2 优雅停机 (Graceful Shutdown) 与 Lifespan 上下文钩子底层原理
FastAPI 早期版本中使用的 `@app.on_event("startup")` 机制由于缺乏异常控制边界，已被官方全面淘汰，转而采用全新的 **Lifespan 上下文管理器** 机制：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动时的逻辑：建立全局数据库或连接池
    yield
    # 2. 关闭时的逻辑：优雅退出扫尾
```
* **控制反转**：整个生命周期在解释器底层包装为一个 Python `generator`。当接收到操作系统的 `SIGTERM`（如 Kubernetes 容器滚动更新、Docker 容器下线）时，FastAPI 不会粗暴终止，而是由 ASGI 网关接手控制。
* **执行路径保证**：首先将应用标记为不可用（不接收新请求），随后挂起、静待正在运行的业务协程处理完毕，最后折返运行 `yield` 之后的扫尾代码（例如干净关闭数据库和 Redis 连接池、清空并导出内存缓存），保障了多节点集群滚动发布时生产环境的 100% 平滑无损过渡。

在操作系统层面，优雅关机（Graceful Shutdown）建立在捕获特定进程中断信号的基础上。例如，当收到 `SIGTERM` 或 `SIGINT` 时，ASGI 服务器首先通知网络监听端口停止接受新的套接字握手。然而，此时可能仍有数十个正在执行的请求协程挂起在事件循环中。基于 Lifespan 架构，FastAPI 允许系统在设定的宽限期内持续轮询执行完内存中的剩余任务，并在协程最终退出的逆向冒泡链路中执行 `finally` 块，最大程度规避了因数据库写事务中途夭折引发的“悬空脏数据”危机。

#### 6.3 生产环境下 Gunicorn 多进程进程管理器与 Uvicorn 工作类协同机制
在实际生产服务器上，如果直接通过终端执行 `uvicorn main:app` 启动，整个 Web 服务仅会消耗并跑在单个物理 CPU 核心上，完全无法压榨多核算力。
工业界的经典部署范式是采用 **Gunicorn 主进程** 结合 **Uvicorn 工作类** 协同工作 [6.1]：
* **Gunicorn 扮演“工头”（Process Manager）**：它不负责真正的客户端网络交互，而只常驻运行在主进程中，专职负责对子工作进程的心跳监控、热加载、故障重新拉起 [6.1]。
* **Uvicorn 扮演“苦力”（UvicornWorker Class）**：通过在 Gunicorn 启动时设定 `--worker-class uvicorn.workers.UvicornWorker`，Gunicorn 会根据物理服务器核心数孵化出 $2N+1$ 个 Uvicorn 工作进程 [6.1]。
* **高并发事件驱动**：每个独立的 Uvicorn Worker 底层都有一个高度调优过的单线程事件循环（基于 `uvloop` C 改写库），由操作系统网络协议栈层面直接分配外部请求，彻底释放了 Python 处理数万级网络并发连接的爆发潜能。

当 Gunicorn 主进程启动并绑定 TCP 端口后，通过底层的 `fork` 系统调用孵化子工作进程。此时，各个 Uvicorn 子进程会天然共享主进程打开的同一个监听套接字描述符（Shared Socket Descriptor），借由操作系统内核提供的 `SO_REUSEPORT` 及网络分发负载均衡，直接在内核态完成向空闲 Uvicorn 进程的请求负载均衡。当某个子工作进程因为外部未捕获致命段错误崩溃退出时，Gunicorn 守护进程会在下一个系统微秒心跳检测到，立即重建健康的工作类副本，确保了系统无间断服务能力。

---

### 2. 双主线项目实战（Guided Mission）

#### 【主线一】个人博客系统 - Phase 6：WebSocket 实时博客弹幕网关与容器集群化

##### 2.1.1 目录结构与准备工作
```text
blog_phase6/
├── templates/
│   └── index.html
├── main.py
├── gunicorn_conf.py
└── Dockerfile
```

##### 2.1.2 路由架构设计
1. 升级网络协议：`WebSocket /api/v1/posts/{post_id}/live-barrage`  
   负责为每一篇文章单独创建持久的长连接“弹幕聊天室”，维持多路并发广播。

##### 2.1.3 开发引导流水线
* **第一步：建立广播控制中心**  
  在 `main.py` 中，定义 `BlogChannelManager` 协调管理器：
  * 使用字典 `self.rooms: Dict[str, List[WebSocket]]` 管理每个文章 ID (房间) 中当前的活动长连接对象。
  * 提供 `join_room`（连接进入房间，接收握手并追加进列表）、`leave_room`（移出关闭的长连接）与 `broadcast_barrage`（并发遍历列表并推送数据）。
* **第二步：编写 WebSockets 持久路由**  
  定义接口 `@app.websocket`，在逻辑内：
  * 触发 `await barrage_manager.join_room()` 接纳新游客。
  * 进入死循环监听：`while True: data = await websocket.receive_text()`。
  * 接收到数据后直接调用 `broadcast_barrage` 发起无阻塞广播推送。

##### 2.1.4 关键逻辑与代码健壮性防线
* **防线一：僵尸断连长连接主动物理释放**  
  在持续监听的死循环中，当客户端发生手动刷新页面、意外断开网络、或物理关机时，`websocket.receive_text()` 会立刻抛出 `WebSocketDisconnect` 异常。
  **如果不加防护，这些死掉的长连接会永久残留在你的 `rooms` 内存中，造成内存物理泄露**。请务必使用 `except WebSocketDisconnect` 捕获该异常，并强制在异常处理块中调用 `leave_room` 释放已死连接。

##### 2.1.5 前端 Vue 3 交互与布局蓝图（WebSocket 双向实时交互）
* **布局设计**：
  * **弹幕大荧幕**：黑色底色框体（具有固定高度，并有 `overflow-y: auto` 垂直滚动条）。
  * **弹幕发布面板**：横向一整排。一个文本框用于填入想要吐嘈的文字，右侧附带一个“发射弹幕”绿色按钮。
* **Vue 3 WebSocket 核心管理流程**：
  1. **建立链接通道**：在 Vue 的 `onMounted` 生命周期钩子内，实例化原生 WebSocket：
     ```javascript
     const ws = new WebSocket(`ws://${window.location.host}/api/v1/posts/fastapi-blog/live-barrage`);
     ```
  2. **事件流监听**：为长连接实例绑定 `ws.onmessage = (event) => {}` 监听。当监听到后端推送的广播消息时，直接将字符串追加进响应式数组 `barrageList`。
  3. **视图刷新绑定**：Vue 检测到列表增长，自动将其遍历挂载到大显示屏上。使用 `nextTick` 保持大显示屏的垂直滚动条始终卡死在最底部。
  4. **双向发射**：在发送按钮的点击事件中，使用 `ws.send(messageText)`，直接通过长连接通道将其发送，不再产生繁重的 HTTP 头通信成本。

---

#### 【主线二】事件竞猜与预测市场 - Phase 6：实时赔率大屏多机容器协同部署

##### 2.2.1 目录结构与准备工作
```text
prediction_phase6/
├── gunicorn_conf.py
├── Dockerfile
├── docker-compose.yml
└── main.py
```

##### 2.2.2 部署架构设计
* 运行底座：使用 Docker 将事件竞猜系统部署在完全隔离的容器化环境中。
* 核心驱动：基于 Gunicorn 启动 Uvicorn 工作进程，让应用程序充分并发跑在多 CPU 核上。
* 网络通信：`WebSocket /api/v1/predictions/{event_id}/odds-feed`  
  当有用户发起 HTTP 下注修改了奖池时，后端将根据最新两方奖池资金配比（如：押 Yes 资金 vs 押 No 资金）重新换算出赔率数据（Odds），并将更新后的赔率消息实时推送至所有连接大屏。

##### 2.2.3 开发引导流水线
* **第一步：实现 WebSocket 实时赔率推送网关**  
  定义 `OddsStreamManager` 协调管理器，维护长连接字典 `self.event_connections: Dict[str, List[WebSocket]]`。
  * 编写 `WebSocket` 协议端点：任何打开赔率大屏的浏览器，在握手成功后都会被追加进该事件的活跃套接字列表。
  * **推送逻辑点拨**：在每次 HTTP 下注端点（如 `db-bet`）成功提交数据库并更新当前事件奖池后，计算该事件最新的赔率分配：`yes_odds = total_pool / yes_pool`。随即调用 `OddsStreamManager` 的异步广播函数，遍历该事件下所有的 WebSocket 实例，分发最新的赔率和奖池占比。
* **第二步：编写 Gunicorn 工业级参数配置**  
  在 `gunicorn_conf.py` 中，根据当前机器物理核心数量自动计算合理的 worker 数量 [6.1]：
  ```python
  import multiprocessing
  bind = "0.0.0.0:8000"
  workers = multiprocessing.cpu_count() * 2 + 1
  worker_class = "uvicorn.workers.UvicornWorker" # 协同核心机制 [6.1]
  ```
* **第三步：编写多阶段分层构建 Dockerfile**  
  采用多阶段（Multi-stage Build）方案编写 `Dockerfile`：
  * **编译阶段（Builder）**：拉取 `python:3.11-slim` 基础镜像，安装依赖，编译出 wheel 包并存储。
  * **运行阶段（Runner）**：再次拉取干净的 slim 镜像，将编译结果直接拷贝进生产运行空间，彻底移除底层编译编译残留物，最大程度压缩最终 Docker 镜像的体积。
  * 启动主命令：`CMD ["gunicorn", "-c", "gunicorn_conf.py", "main:app"]` [6.1]。
* **第四步：编写 docker-compose 编排声明**  
  定义 `docker-compose.yml` 描述。将容器内暴露出的 `8000` 端口映射给物理主机的 `8000`。设置存储卷 `volumes`，将 SQLite 数据库文件映射到容器外部，保证服务容器销毁更新时数据绝对不丢失。

##### 2.2.4 关键逻辑与代码健壮性防线
* **防线一：生产级多核心下的状态共享防爆**  
  由于使用了 Gunicorn 多工作进程模式 [6.1]，每一个 Uvicorn Worker 本质上是一个处于独立沙盒内存中的 OS 进程。
  **避坑点**：多进程启动后，每个进程内部的 `OddsStreamManager` 只能访问和推送连接到自己进程上的部分浏览器，无法对全局连接执行推送。
  * 开发者应明确认识到：在多核多进程部署（或集群多机部署）环境下，纯 Python 内存级 Channel Manager 将失效。高并发预测市场的正确落地架构是必须引入外部轻量级 Pub/Sub 广播机制（如使用 Redis 的 `SUBSCRIBE` / `PUBLISH` 指令或搭配消息中间件）。将单机进程广播升级为跨进程的网络消息分发，解决多核并发下的推送孤岛瓶颈。

##### 2.2.5 前端 Vue 3 交互与布局蓝图（WebSocket 实时数据大屏）
* **布局设计**：
  * **实时赔率荧光板**：左侧巨型红色字体显示“押 Yes 最新赔率”，右侧巨型绿色字体显示“押 No 最新赔率”。
  * 赔率波动曲线背景：大屏底色使用深色。
* **Vue 3 核心状态与行为驱动逻辑**：
  1. **建立实时连接**：
     ```javascript
     const ws = new WebSocket(`ws://${window.location.host}/api/v1/predictions/tomorrow-rain/odds-feed`);
     ```
  2. **动效捕获刷新**：监听 `ws.onmessage`。一旦收到服务端因为新下注而广播的赔率更新包，即时通过 Vue 3 响应式系统替换当前大屏上的赔率数值。

---

### 3. 本模块实战小作业

#### 3.1 作业目标：系统指标采集与实时监控 WebSocket 接口
开发一个独立的服务器物理资源监测长连接网关。用户在打开监控后台时，后端需要实时、周期性地提取服务器当前的 CPU 占用率与内存消耗比值，并以 WebSocket 主动广播的形式，源源不断地推送更新大荧幕前端组件。

#### 3.2 技术引导与架构点拨
* 先安装系统指标分析组件：`pip install psutil`。
* 编写一个独立的 `WebSocket` 路由。在死循环中，利用 `psutil.cpu_percent()` 提取实时数据。
* **避坑点**：在死循环中，必须使用非阻塞的协程休眠 `await asyncio.sleep(1)`，千万不要误写成同步的 `time.sleep(1)`。如果是同步休眠，整个事件循环都将在那 1 秒钟内彻底死锁，造成全局接口挂起。

#### 3.3 健壮性防线
* 确保针对 `psutil` 读取指标的过程和 `send_json()` 推送的过程使用了标准的断连捕获，使得哪怕只是浏览器窗口一闭合，也能够让后台监控协程安全退出、并干净地回收该进程下的所有资源。

---

🏆 **恭喜您！如果您脚踏实地完成了这 2 个渐进式主线项目（从最基础的动态路由，到 DTO 洗涤校验、类生命周期依赖、HMAC 密码验证、SQLAlchemy 悲观锁事务控防、WebSocket 长连接广播、最终容器集群化部署），您就已经具备了应对中高级 Python 架构开发和企业复杂场景需求的深厚底气！**