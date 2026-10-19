from pydantic import BaseModel

class User_conversation(BaseModel):
    question:str
    #response:str
    session_id:str