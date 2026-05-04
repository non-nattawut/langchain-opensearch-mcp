import os
import asyncio
import traceback
import json
from typing import List

import atexit
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from dotenv import load_dotenv

from constant.AIResponse import AIResponse
from services.mcp_service import MCPService
from services.llm_factory import LLMFactory
from services.skill_service import SkillService

load_dotenv()

class LLMService:
    def __init__(self):
        # Initialize basic components
        self.llm = LLMFactory.create_llm()
        self.mcp_service = MCPService()
        self.system_prompt = SkillService.load_skills()
        self.tools = []

        # Set the loop as current for this thread (Streamlit usually runs in threads)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Initialize MCP and Agent synchronously during object creation
        try:
            print(f"Initializing MCP tools and Agent for {os.getenv('LLM_PROVIDER', 'NVIDIA')}...")
            # Use run_until_complete to execute the async tool fetching
            self.tools = self.loop.run_until_complete(self.mcp_service.get_tools_async())
            print("MCP Tools initialized successfully.")
        except Exception as e:
            print(f"Error during MCP Tools initialization: {e}")
            traceback.print_exc()
        finally:
            self.agent = create_agent(
                self.llm,
                tools=self.tools,
                system_prompt=self.system_prompt
            )

    async def astream_response(self, message: str, chat_history=None):
        """Asynchronous stream response that handles the tool-calling loop."""
        try:
            inputs = {"messages": chat_history + [HumanMessage(name="user", content=message)]}
            accumulate_tool_call = None
            print("======= prompt log =======")
            print(message)

            if self.agent:
                print("======= AI message log =======")
                async for chunk in self.agent.astream(inputs, stream_mode="messages"):
                    msg, metadata = chunk
                    if msg.content or msg.tool_calls:
                        print(msg) # log

                    if isinstance(msg, AIMessage) and msg.content:
                        content = msg.content
                        if isinstance(content, str):
                            yield {"type": AIResponse.TEXT, "content": content}
                        elif isinstance(content, List): # handle GEMINI response
                            yield {"type": AIResponse.TEXT, "content": content[0].get("text")}

                    elif isinstance(msg, AIMessage) and not msg.content and msg.tool_calls:
                        if accumulate_tool_call is None:
                            accumulate_tool_call = msg
                        else:
                            accumulate_tool_call += msg

                    elif isinstance(msg, ToolMessage):
                        if accumulate_tool_call:
                            yield {"type": AIResponse.TOOL_CALL,
                                   "content": accumulate_tool_call}

                            name = accumulate_tool_call.tool_calls[0].get("name", "Unknown Tool")
                            args = accumulate_tool_call.tool_calls[0].get("args", {})
                            yield {"type": AIResponse.FORMATTED_TOOL_LOG,
                                   "content": f"️🛠️ Calling tool: {name}\n\n"}

                            formatted_args = json.dumps(args, indent=2, ensure_ascii=False)
                            yield {"type": AIResponse.FORMATTED_TOOL_LOG,
                                   "content": f"**Arguments:**\n"
                                              f"```json\n{formatted_args}\n```\n"}

                            accumulate_tool_call = None

                        try:
                            data = json.loads(msg.content)
                            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                            yield {"type": AIResponse.FORMATTED_TOOL_LOG,
                                   "content": f"✅ Tool {msg.name}\n\n"
                                              f"**Response:**\n"
                                              f"```json\n{formatted_json}\n```\n"}
                        except (json.JSONDecodeError, TypeError):
                            yield {"type": AIResponse.FORMATTED_TOOL_LOG,
                                   "content": f"✅ Tool {msg.name}\n\n"
                                              f"**Response:**\n"
                                              f"```json\n{msg.content}\n```\n"}
                        finally:
                            yield {"type": AIResponse.TOOL_RESPONSE,
                                   "content": msg}
            else:
                async for chunk in self.llm.astream(inputs, stream_mode="messages"):
                    yield {"type": AIResponse.TEXT, "content": chunk.content}

        except Exception as e:
            traceback.print_exc()
            yield {"type": AIResponse.TEXT, "content": f"\n\n**Error:** {str(e)}"}

    def stream_response(self, message: str, chat_history=None):
        """Synchronous wrapper for astream_response to make it compatibility with Streamlit loop."""
        asyncio.set_event_loop(self.loop)

        gen = self.astream_response(message, chat_history)
        while True:
            try:
                yield self.loop.run_until_complete(anext(gen))
            except StopAsyncIteration:
                break

    # def shutdown(self):
    #     """Gracefully close the MCP server and the event loop."""
    #     print("\nShutting down LLM Service and closing MCP connections...")
    #     try:
    #         self.loop.run_until_complete(self.mcp_service.cleanup())
    #         self.loop.stop()
    #         self.loop.close()
    #         print("Shutdown complete.")
    #     except Exception as e:
    #         pass