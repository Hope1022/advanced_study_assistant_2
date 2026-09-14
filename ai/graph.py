from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from ai.ai_ import llm_node, judge_node, safe_node, unsafe_node, route
from ai.state import State
import sys
sys.path.insert(0, r"d:\AI engineering\AI_FOR_RURAL\G_9 biology")
# class State(TypedDict):
#     query:str
#     context:str
#     response:str
#     is_valid:bool

graph = StateGraph(State)

graph.add_node("call_llm",llm_node)
graph.add_node("judge",  judge_node)
graph.add_node("safe",   safe_node)
graph.add_node("unsafe", unsafe_node)

graph.add_edge(START, "call_llm")
graph.add_edge("call_llm","judge")
graph.add_conditional_edges("judge", route, {"safe": "safe", "unsafe": "unsafe"})
graph.add_edge("safe",   END)
graph.add_edge("unsafe", END)

app= graph.compile()
# query = "what is a membrane-bound nucleus"
# result = app.invoke({
#         "query":query,
#         "context": "",
#         "response":  "",
#         "is_safe": False
#     })
    
# print(result["response"])