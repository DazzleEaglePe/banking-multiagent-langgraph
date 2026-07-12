import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Load environment variables
load_dotenv()

# Configure Google GenAI key
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise ValueError("GEMINI_API_KEY is not configured in .env file.")

genai.configure(api_key=gemini_key)

# Global LlamaIndex Settings (for the RAG tool)
Settings.llm = Gemini(model="models/gemini-flash-lite-latest", api_key=gemini_key, temperature=0.0)
Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-001", api_key=gemini_key)

# Patched LangChain clients to avoid gRPC timeouts and argument conflicts
class CustomChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # Prevent LangGraph/Ragas from sending unexpected params
        kwargs.pop("temperature", None)
        kwargs.pop("n", None)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

class CustomGoogleGenerativeAIEmbeddings(GoogleGenerativeAIEmbeddings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from langchain_google_genai._genai_extension import build_generative_service
        # Handle string or secret type for API Key
        api_key_str = self.google_api_key.get_secret_value() if hasattr(self.google_api_key, 'get_secret_value') else self.google_api_key
        self.client = build_generative_service(
            api_key=api_key_str,
            transport='rest'
        )

def get_chat_model():
    """Returns a patched LangChain Chat Model for Gemini Flash Lite."""
    return CustomChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest", 
        google_api_key=gemini_key, 
        max_retries=10
    )

def get_embeddings_model():
    """Returns a patched LangChain Embeddings Model with REST transport."""
    return CustomGoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", 
        google_api_key=gemini_key
    )
