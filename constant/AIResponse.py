from enum import Enum


class AIResponse(Enum):
    TEXT = "TEXT",
    FORMATTED_TOOL_LOG = "FORMATTED_TOOL_LOG",
    TOOL_CALL = "TOOL_CALL",
    TOOL_RESPONSE = "TOOL_RESPONSE"