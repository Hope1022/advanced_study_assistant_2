import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from ai.state import AgentState
from ai.llm import llm
from ai.chunk import final_chunk
from ai.ai_service import summarize_history, build_retrieval_query
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import GoogleSerperAPIWrapper
from ai.chunk import sub_querries
serper = GoogleSerperAPIWrapper()
load_dotenv()
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a biology tutor assistant for Grade 9 students.
- Use ONLY the context below to answer.
- Regular greetings are okay.
- Maximum 10 lines of response.
- Explain it supersimply as if the user is 7 years old.
If the context is empty or not relevant:
- You may answer from your own knowledge
- But you MUST say "Based on my general knowledge:" before answering
- Never make up specific facts, numbers, or names
- If truly unsure, say so

Context:
{context}

Previous summary:
{summary}

Recent conversation:
{history}
"""),
        ("human", "{question}"),
    ]
)

llm_chain = prompt_template|llm|StrOutputParser()
MAX_MESSAGES = 6  
SUMMARY_THRESHOLD = 10
ROUTER_SYSTEM_PROMPT = """You are a routing assistant for a Grade 9 biology student assistant.

Your ONLY job is to decide which function to call based on the student's message.
Do not answer the question yourself. Just pick the right function.

Rules:
- curriculum_function  → for any biology curriculum question, concept explanation,or anything related to the Grade 9 biology textbook.
- web_search_function  → when the student asks for extra resources, videos,articles, links, or anything from the internet.
- exercise_function    → when the student asks for practice questions, a quiz,exercises, or wants to test their knowledge.
Always pick one function. Never respond directly.
never right it in dictionary, just say the function name only
"""
async def router_node(state: AgentState) -> AgentState:
    question = state["question"]
    history = state["history"]

    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-6:]
    )

    response =await llm.ainvoke([
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Previous conversation:
{history_text}
    
Student question: {question}
        """)
    ])
    
    route = response.content.strip().lower()
    print(route)
    return {"route": route}

def decide_route(state: AgentState) -> str:
    route= state["route"]

    if route in ["web_search_function", "exercise_function"]:
        return route

    return "curriculum_function" 

def web_search_node(state: AgentState) -> AgentState:
    final_query = ""
    question = state["question"]
    multiple_question = sub_querries(question)
    for a in multiple_question:
        final_query +=","+a
      
    print(final_query)
    raw = serper.results(final_query)
    organic = raw.get("organic", [])

    lines = []
    for i, r in enumerate(organic[:5], start=1):
        title = r.get("title", "No title")
        link = r.get("link", "")
        lines.append(f"{i}. {title}\n   {link}")

    results = "\n".join(lines)
    
    

    return {"response": results}


def exercise_node(state: AgentState) -> AgentState:
    question = state["question"]

    # TODO: replace with your real exercise generation implementation
    result = "exercise"

    return {"response": result}

async def curriculum_node(state:AgentState):
   history = state["history"]
   query = state["question"]
   if len(history) > SUMMARY_THRESHOLD:
        summary = summarize_history(history[:-MAX_MESSAGES])
        recent_history = history[-MAX_MESSAGES:]
   else:
        summary = ""
        recent_history = history[-MAX_MESSAGES:]

    # format recent history as a string
   history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in recent_history
    )
   retrieval_query = build_retrieval_query(query, recent_history)
   context = final_chunk(retrieval_query)
   response_parts = []
   async for chunk in llm_chain.astream({
        "context": context,
        "question": query,
        "history": history_text,
        "summary": summary,
   }, config={"tags": ["curriculum_answer"]}):
      response_parts.append(chunk)
   
   result = "".join(response_parts)
   
   return {"response": result}