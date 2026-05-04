# OpenSearch LLM Chat with Model Context Protocol (MCP) and Streamlit UI

This project demonstrates an intelligent chat application that leverages Large Language Models (LLMs) to interact with OpenSearch data. It uses LangChain for orchestrating LLM interactions and the Model Context Protocol (MCP) for seamless integration with OpenSearch. The user interface is built with Streamlit, providing an intuitive chat experience.

## Features:
- **LLM Integration**: Connects to various LLM providers (NVIDIA, Gemini, LM Studio, DeepSeek) for natural language understanding and generation.
- **OpenSearch Interaction**: Utilizes the Model Context Protocol (MCP) to query and retrieve data from OpenSearch clusters.
- **Tool-use Capabilities**: LLMs can intelligently decide when to use OpenSearch tools to fulfill user requests.
- **Streamlit UI**: A user-friendly web interface for chatting with the LLM and viewing tool interactions.
- **Configurable Providers**: Easily switch between different LLM providers via environment variables.

## Getting Started

Follow these steps to set up and run the application.

### Prerequisites

-   Docker and Docker Compose installed.
-   Python 3.9+
-   `uv` (or `pip`) for dependency management.

### 1. Configure Environment Variables

Create a `.env` file by copying the provided example and fill in your API keys and OpenSearch details.

```bash
cp .env.example .env
```

Edit the `.env` file:
-   Set `LLM_PROVIDER` to your desired LLM (e.g., `NVIDIA`, `GEMINI`, `LMSTUDIO`, `DEEPSEEK`).
-   Provide the necessary API keys and model names for your chosen provider (e.g., `NVIDIA_API_KEY`, `GOOGLE_API_KEY`, etc.).
-   Configure your OpenSearch connection details (`OPENSEARCH_URL`, `OPENSEARCH_USERNAME`, `OPENSEARCH_PASSWORD`).

### 2. Run OpenSearch (via Docker Compose)

Start your OpenSearch instance using Docker Compose. This will set up a local OpenSearch cluster that the application can connect to.

```bash
docker compose up -d
```

Wait for OpenSearch to fully start up before proceeding. You can check its status with `docker compose ps`.

### 3. Install Dependencies and Run the Streamlit App

First, install the project dependencies. It's recommended to use a virtual environment.

```bash
# Create a virtual environment (if you haven't already)
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install dependencies using uv (or pip)
uv sync
# or
# pip install -r requirements.txt
```

Now, run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

Your browser should automatically open to the Streamlit application. If not, navigate to `http://localhost:8501` (or the address shown in your terminal).

Enjoy chatting with your OpenSearch-powered LLM assistant! ✨
