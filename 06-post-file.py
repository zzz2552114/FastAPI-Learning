class File_Message(BaseModel):
    filename: str = Field(...)
    filetype: str
    filesize_byte: int


class Request_Message(BaseModel):
    header: str
    cookie: dict
    method: Literal['GET', 'POST']


class Message(BaseModel):
    file_info: File_Message
    request_info: Request_Message


@app.post('/file')
async def post_file(file: UploadFile = File(), request: Request = None) -> Message:
    with open(file.filename, "wb") as f:
        while True:
            content = await file.read(1024 * 1024)
            if not content:
                break
            f.write(content)

    file_message = File_Message(
        filename=file.filename,
        filetype=file.content_type,
        filesize_byte=file.size
    )
    head = str(request.headers)
    request_message = Request_Message(
        header=head,
        cookie=request.cookies,
        method=request.method
    )
    message = Message(
        file_info=file_message,
        request_info=request_message
    )
    print(file_message)
    print(request_message)
    print(message)
    await file.close()
    return message