from typing import TypedDict
class State(TypedDict):
    query:str
    context:str
    response:str
    is_safe:bool

