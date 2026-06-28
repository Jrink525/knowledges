    # "text" | "file" | "data"
    text: str | None = None
    data: dict | None = None
    mimeType: str | None = None
    uri: str | None = None


class Message(BaseModel):
    role: str           # "user" | "agent"
