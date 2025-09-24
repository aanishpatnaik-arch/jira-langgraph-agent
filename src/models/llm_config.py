from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

class LLMConfig:
    @staticmethod
    def get_llm():
        llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE
        )
        print("Gemini initialized successfully.")
        return llm
