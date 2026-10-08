import os
from typing import Any, Dict

from app.mcp_registry import MCPRegistry


class MCPClient:
    def __init__(self):
        self.registry = MCPRegistry()

    async def list_tools(self) -> dict[str, Any]:
        return await self.registry.list_tools()

    async def get_tools_status(self) -> dict[str, bool]:
        return {name: bool(meta.get("enabled")) for name, meta in self.registry.registry.items()}

    async def call_tool(self, server: str, tool_name: str, payload: Dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.registry.call_tool(server=server, tool_name=tool_name, payload=payload)
