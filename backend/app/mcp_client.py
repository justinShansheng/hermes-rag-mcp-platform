import httpx


class MCPClient:
    def __init__(self):
        self.base_url = "http://localhost:3001"

    async def list_tools(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/tools")
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass

        return {
            "servers": [
                {"name": "filesystem", "status": "not_connected"},
                {"name": "github", "status": "not_connected"},
                {"name": "web_search", "status": "not_connected"},
            ]
        }

    async def get_tools_status(self) -> dict:
        return {
            "filesystem": True,
            "github": True,
            "web_search": True,
        }
