from ai.chunk import retrieve
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from ai.state import State
import sys
sys.path.insert(0, r"d:\AI engineering\AI_FOR_RURAL\G_9 biology")
llm = ChatOllama(
    model="qwen2.5:1.5b"
)

def llm_node(state:State):
    context = retrieve(state["query"])

    answer = llm.invoke([
        SystemMessage(content=f"""You are a biology tutor for Grade 9 students.
Use ONLY the context below to answer.
-10 lines of maximum response 
-explain it supersimply as if the user is 7 years old
If the answer is not in the context say I don't have enough information.

Context:
{context}"""),
        HumanMessage(content=state["query"])
    ])

    return {
       
        "context": context,
        "response":  answer.content
    }

def judge_node(state:State):
    # llm_response = state["response"]
    
    verdict = llm.invoke([
        SystemMessage(content=f"""You are a fact checker.
Reply with only one word.
GROUNDED if the answer is fully supported by the context.
HALLUCINATED if the answer contains anything not in the context.

Context:
{state["context"]}"""),
        HumanMessage(content=state["response"])
    ])

    is_safe = "GROUNDED" in verdict.content.upper()

    return {"is_safe": is_safe}
def route(state: State):
    if state["is_safe"]:
        return "safe"
    return "unsafe"
def safe_node(state: State):
    return {"answer": state["response"]}


def unsafe_node(state: State):
    return {"answer": "I could not verify this answer from the textbook. Please consult your teacher."}