from fastapi import FastAPI
from fastapi.responses import FileResponse
from schema import User_conversation
import sys
import os
from ai.ai_ import ask
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai"))


app = FastAPI()


@app.get("/")
def home():
    return FileResponse("ui/index.html")

@app.post("/ask")
def chat(query: User_conversation):
    answer = ask(query.question, query.session_id)
    return {"answer": answer}