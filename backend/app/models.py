from pydantic import BaseModel
from typing import Optional, List


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    username: str
    password: str


class SessionCreate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None


class MessageCreate(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    model: Optional[str] = None
    session_id: Optional[str] = None


class ToolCallRequest(BaseModel):
    server: str
    tool: str
    args: Optional[dict] = None


class RAGIndexRequest(BaseModel):
    files: List[str]


class AdminUpdateRoleRequest(BaseModel):
    role: str  # 'user' or 'admin'
