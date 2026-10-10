import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()
groq_api_key = os.getenv("groq_api_key")
# class AgentState(TypedDict):
#     question: str
#     history: list[dict]
#     route: str
#     response: str

llm = ChatGroq(api_key=groq_api_key,
               model="openai/gpt-oss-120b")