from pydantic import BaseModel

class User_conversation(BaseModel):
    question:str
    answer:str
    #response:str
    # session_id:str