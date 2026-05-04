import os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv

load_dotenv()

class MCPService:
    def __init__(self, command="uv", args=None, env=None):
        self.server_params = StdioServerParameters(
            command=command,
            args=args or ["tool", "run", "opensearch-mcp-server-py"],
            env=env or os.environ.copy()
        )
        # object that keeps context managers open
        self.exit_stack = AsyncExitStack()
        self.tools = []
        self.is_initialized = False

    async def get_tools_async(self):
        """Initializes the connection ONCE and keeps it open permanently."""
        if self.is_initialized:
            return self.tools

        try:
            # 1. Enter the stdio_client context and KEEP IT OPEN
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )
            # 2. Enter the ClientSession context and KEEP IT OPEN
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )

            await session.initialize()
            self.tools = await load_mcp_tools(session)
            self.is_initialized = True

            return self.tools

        except Exception as e:
            print(f"Failed to initialize MCP: {e}")
            return []

    # async def cleanup(self):
    #     """Call this only when shutting down your app to cleanly close the server."""
    #     await self.exit_stack.aclose()