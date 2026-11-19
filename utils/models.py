import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in .env")

model = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0
)
