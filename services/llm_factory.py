import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

class LLMFactory:
    @staticmethod
    def create_llm():
        provider = os.getenv("LLM_PROVIDER", "NVIDIA").upper()
        temperature = float(os.getenv("LLM_TEMPERATURE", 0.2))
        top_p = float(os.getenv("LLM_TOP_P", 0.7))

        match provider:
            case "NVIDIA":
                return ChatNVIDIA(
                    model=os.getenv("NVIDIA_MODEL"),
                    nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
                    temperature=temperature,
                    top_p=top_p
                )
            case "GEMINI":
                return ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    temperature=temperature,
                    top_p=top_p
                )
            case "LMSTUDIO":
                return ChatOpenAI(
                    base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
                    api_key=SecretStr(os.getenv("LMSTUDIO_API_KEY", "not-needed")),
                    model=os.getenv("LMSTUDIO_MODEL", "local-model"),
                    temperature=temperature,
                    top_p=top_p
                )
            case "DEEPSEEK":
                return ChatOpenAI(
                    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                    api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY", "")),
                    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                    temperature=temperature,
                    top_p=top_p
                )
            case _:
                raise ValueError(f"Unsupported LLM provider: {provider}")
