from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_core.tools import tool
from collections.abc import AsyncIterator
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
#from ai.tools import curriculum_tool,web_search_tool,exercise_tool  
# from typing import TypedDict
from ai.nodes import curriculum_node, web_search_node,exercise_node,router_node,decide_route
from ai.state import AgentState



    




def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router",     router_node)
    graph.add_node("curriculum_node", curriculum_node)
    graph.add_node("web_search_node", web_search_node)
    graph.add_node("exercise_node",   exercise_node)
    
    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        decide_route,
        {
            "curriculum_function": "curriculum_node",
            "web_search_function": "web_search_node",
            "exercise_function":   "exercise_node",
            
        }
    )

    graph.add_edge("curriculum_node", END)
    graph.add_edge("web_search_node", END)
    graph.add_edge("exercise_node",   END)
    # graph.add_edge("fallback_node",   END)

    return graph.compile()


agent = build_graph()
async def run_agent(
    question: str,
    history: list[dict],
) -> AsyncIterator[tuple[str, str]]:
    inputs = {
        "question": question,
        "history": history,
        "route": "",
        "response": "",
    }
    streamed_response = False
    active_node = None
    node_status = {
        "router": "Routing...",
        "curriculum_node": "Fetching chunks...",
        "web_search_node": "Searching the web...",
        "exercise_node": "Preparing exercises...",
    }

    async for event in agent.astream_events(inputs, version="v2"):
        event_name = event["event"]
        node_name = event.get("metadata", {}).get("langgraph_node")

        if (
            event_name == "on_chain_start"
            and node_name in node_status
            and node_name != active_node
        ):
            active_node = node_name
            yield "status", node_status[node_name]

        if (
            event_name == "on_chat_model_stream"
            and node_name == "curriculum_node"
            and "curriculum_answer" in event.get("tags", [])
        ):
            chunk = event["data"]["chunk"]
            content = chunk.content
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "".join(
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and isinstance(block.get("text"), str)
                )
            else:
                text = ""

            if text:
                streamed_response = True
                yield "token", text

        elif event_name == "on_chain_end" and node_name in {
            "curriculum_node",
            "web_search_node",
            "exercise_node",
        }:
            output = event["data"].get("output")
            if isinstance(output, dict):
                response = output.get("response")
                if (
                    isinstance(response, str)
                    and response
                    and (node_name != "curriculum_node" or not streamed_response)
                ):
                    yield "token", response
