from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature = 0.3,
    google_api_key = os.getenv("GEMINI_API_KEY")
)


response = llm.invoke(
    "Explain LangGraph in one sentence"
)

print(response.content)
