from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ai.chunk import final_chunk
from langchain_core.runnables import RunnableBranch, RunnableLambda
import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("groq_api_key")
#llm = ChatOllama(model="qwen2.5:1.5b")
llm = ChatGroq(api_key=groq_api_key,
               model="openai/gpt-oss-20b")
prompt_template = ChatPromptTemplate.from_messages(
    [("system","""You are a biology tutor assistant for Grade 9 students.
-Use ONLY the context below to answer.
-If the answer is not in the context, and not related to biology education context, say I don't have enough information. 
Context:
{context} 
-regular greetings are okay
-maximum 10 lines of response 
-explain it supersimply as if the user is 7 years old


"""), ("human","{question}")]
)
judge_template = ChatPromptTemplate.from_messages([
    ("system", """You are a classifier. Your only job is to output exactly one word.
     Context: {context}
Output GROUNDED if the user prompt only uses information from the context.
Output HALLUCINATED if the user prompt contains anything not in the context and not related to biology.
Do not explain. Do not add punctuation. Output only one word."""),
    ("human", "{result}")
])
# question = "how are insects useful for our environment"
llm_chain = prompt_template|llm|StrOutputParser() 

def call_llm(query):
   context = final_chunk(query)
   result = llm_chain.invoke({
       "context": context,
       "question":query
   })
   
   return result
# judge_chain = judge_template | llm | StrOutputParser()

# result = llm_chain.invoke({
#     "context":context,
#     "question":question})
# verdict = judge_chain.invoke({"context": context, "result": result})
# print(result)
# from langsmith import Client
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
# os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")

# client = Client()
# print("Connected:", client.list_projects())
