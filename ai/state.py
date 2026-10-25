from typing import TypedDict

class AgentState(TypedDict):
    question: str
    history: list[dict]
    route: str
    response: str
