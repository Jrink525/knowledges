    # "user" | "agent"
    parts: list[Part]


class TaskStatus(BaseModel):
    state: str          # submitted | working | input-required | completed | failed
