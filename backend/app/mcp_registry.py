import os
from typing import Any, Dict

import httpx


class MCPRegistry:
    def __init__(self):
        self.registry = {
            "filesystem": {
                "enabled": True,
                "tools": ["list_dir", "read_file"],
            },
            "github": {
                "enabled": True,
                "tools": ["repo_info", "search_repo"],
            },
            "web_search": {
                "enabled": True,
                "tools": ["search"],
            },
        }

    async def list_tools(self) -> dict[str, Any]:
        return {
            "servers": [
                {
                    "name": name,
                    "status": "ready" if meta.get("enabled") else "disabled",
                    "tools": meta.get("tools", []),
                }
                for name, meta in self.registry.items()
            ]
        }

    async def call_tool(self, server: str, tool_name: str, payload: Dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}

        if server == "filesystem":
            return await self._filesystem_tool(tool_name, payload)
        if server == "github":
            return await self._github_tool(tool_name, payload)
        if server == "web_search":
            return await self._web_search_tool(tool_name, payload)

        return {
            "server": server,
            "tool": tool_name,
            "status": "unsupported",
            "result": "This MCP server is not yet implemented.",
        }

    async def _filesystem_tool(self, tool_name: str, payload: Dict[str, Any]) -> dict[str, Any]:
        if tool_name == "list_dir":
            base = payload.get("path", ".")
            entries = []
            for item in sorted(os.listdir(base)):
                full = os.path.join(base, item)
                entries.append({"name": item, "is_dir": os.path.isdir(full)})
            return {"server": "filesystem", "tool": tool_name, "status": "ok", "result": entries}

        if tool_name == "read_file":
            file_path = payload.get("path")
            if not file_path or not os.path.exists(file_path):
                return {"server": "filesystem", "tool": tool_name, "status": "error", "result": "Missing file path."}
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                return {"server": "filesystem", "tool": tool_name, "status": "ok", "result": fh.read(2000)}

        return {"server": "filesystem", "tool": tool_name, "status": "unsupported", "result": "Unsupported filesystem tool."}

    async def _github_tool(self, tool_name: str, payload: Dict[str, Any]) -> dict[str, Any]:
        repo = payload.get("repo") or "justinShansheng/hermes-rag-mcp-platform"

        if tool_name == "repo_info":
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(f"https://api.github.com/repos/{repo}")
                response.raise_for_status()
                return {"server": "github", "tool": tool_name, "status": "ok", "result": response.json()}

        if tool_name == "search_repo":
            query = payload.get("query") or "hermes agent"
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get("https://api.github.com/search/repositories", params={"q": query, "per_page": 5})
                response.raise_for_status()
                return {"server": "github", "tool": tool_name, "status": "ok", "result": response.json().get("items", [])}

        return {"server": "github", "tool": tool_name, "status": "unsupported", "result": "Unsupported GitHub tool."}

    async def _web_search_tool(self, tool_name: str, payload: Dict[str, Any]) -> dict[str, Any]:
        if tool_name != "search":
            return {"server": "web_search", "tool": tool_name, "status": "unsupported", "result": "Unsupported web search tool."}

        query = payload.get("query") or "Hermes Agent"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            response.raise_for_status()
            data = response.json()

        return {
            "server": "web_search",
            "tool": tool_name,
            "status": "ok",
            "result": {
                "topic": data.get("Heading"),
                "abstract": data.get("Abstract"),
                "related_topics": data.get("RelatedTopics", [])[:5],
            },
        }
