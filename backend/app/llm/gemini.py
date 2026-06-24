from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

class SafeChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    def invoke(self, *args, **kwargs):
        response = super().invoke(*args, **kwargs)
        if hasattr(response, 'content') and isinstance(response.content, list):
            parts = []
            for part in response.content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
            response.content = "".join(parts)
        return response

llm = SafeChatGoogleGenerativeAI(
    model = "gemini-3.1-flash-lite",
    temperature = 0.3,
    google_api_key = os.getenv("GEMINI_API_KEY")
)


# LLM instance initialized, ready to be imported.
