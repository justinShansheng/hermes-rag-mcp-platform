from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    model: str | None = None
    session_id: str | None = None


class SessionCreate(BaseModel):
    title: str = Field(default="New session")
    model: str | None = None


class MCPToolCallRequest(BaseModel):
    server: str
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)


class UploadResponse(BaseModel):
    status: str
    filename: str
    path: str


class RagIndexRequest(BaseModel):
    files: list[str] = Field(default_factory=list)


class ToolInfo(BaseModel):
    name: str
    status: str
    tools: list[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    mode: str | None = None


class ModelCatalog(BaseModel):
    local: list[str]
    cloud: list[str]


class ToolResult(BaseModel):
    server: str
    tool: str
    status: str
    result: Any
