from pydantic import BaseModel
from datetime import datetime


class ConversationCreateSchema(BaseModel):
    title: str | None = None


class ConversationResponseSchema(BaseModel):
    id: int
    title: str | None
    created_at: datetime


class MessageCreateSchema(BaseModel):
    content: str


class MessageResponseSchema(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime