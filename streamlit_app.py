import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from constant.AIResponse import AIResponse
from services.llm_service import LLMService

role_user = "user"
role_assistant = "assistant"

st.set_page_config(page_title="Open Search MCP LLM Chat", page_icon="🤖")
st.title("Open Search MCP LLM Chat")

# Initialize the service
if "llm_service" not in st.session_state:
    st.session_state.llm_service = LLMService()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history_include_tool_log" not in st.session_state:
    st.session_state.chat_history_include_tool_log = []

# Sidebar options
with st.sidebar:
    st.markdown("### Chat Controls")
    if st.button("➕ New Chat / Clear History"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages from history on app rerun or when user query
for chat_history_include_tool_log in st.session_state.chat_history_include_tool_log:
    with st.chat_message(chat_history_include_tool_log.get("role")):
        st.markdown(chat_history_include_tool_log.get("content"))

# User input
if prompt := st.chat_input("What is on your mind?"):
    # Display user message in chat message container
    prompt = prompt.strip()
    with st.chat_message(role_user):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message(role_assistant):
        message_placeholder = st.empty()
        full_display_response = ""
        pure_ai_text = ""
        tool_messages = []

        # Stream chat response
        for chunk in st.session_state.llm_service.stream_response(prompt, st.session_state.messages):
            chunk_type = chunk.get("type")
            chunk_content = chunk.get("content", "")

            # Add to what the user sees on screen
            if chunk_type in [AIResponse.TEXT, AIResponse.FORMATTED_TOOL_LOG]:
                full_display_response += chunk_content
                message_placeholder.markdown(full_display_response + "▌")

            if chunk_type == AIResponse.TEXT:
                pure_ai_text += chunk_content
            elif chunk_type in [AIResponse.TOOL_CALL, AIResponse.TOOL_RESPONSE]:
                tool_messages.append(chunk_content)

        message_placeholder.markdown(full_display_response)

    # Add messages to chat history
    st.session_state.chat_history_include_tool_log.append({"role": role_user, "content": prompt})
    st.session_state.chat_history_include_tool_log.append({"role": role_assistant, "content": full_display_response})

    # Add messages to chat history exclude request/response JSON and include tool call and response for LLM
    st.session_state.messages.append(HumanMessage(name=role_user, content=prompt))
    for tool in tool_messages:
        st.session_state.messages.append(tool)
    st.session_state.messages.append(AIMessage(name=role_assistant, content=pure_ai_text))
