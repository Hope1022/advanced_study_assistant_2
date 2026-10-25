# import json
# import pdfplumber
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings
# # from langchain_community.embeddings import OllamaEmbeddings
# import os
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma
# from langchain_experimental.text_splitter import SemanticChunker
# #from sentence_transformers import CrossEncoder
# from flashrank import Ranker, RerankRequest

# embeddings = OllamaEmbeddings(model="nomic-embed-text")
# # reranker   = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")

# if not os.path.exists("./biology_db") or not os.listdir("./biology_db"):

#     pages = []
#     with pdfplumber.open("books/Biology_9.pdf") as pdf:
#         for i, page in enumerate(pdf.pages):
#             text = page.extract_text()
#             if text and text.strip():
#                 pages.append(Document(
#                     page_content=text,
#                     metadata={"page": i + 1, "type": "text"}
#                 ))

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=100
#     )
#     text_docs = splitter.split_documents(pages)

#     with open("chart_annotations.json") as f:
#         charts = json.load(f)
#     with open("table_summaries.json") as f:
#         tables = json.load(f)

#     json_docs = []
#     for entry in charts + tables:
#         json_docs.append(Document(
#             page_content=entry["description"],
#             metadata={
#                 "id":      entry["id"],
#                 "page":    entry["page"],
#                 "type":    entry["type"],
#                 "topic":   entry["topic"],
#                 "chapter": entry["chapter"],
#                 "grade":   entry["grade"],
#                 "subject": entry["subject"]
#             }
#         ))

#     all_docs = text_docs + json_docs

#     db = Chroma.from_documents(
#         documents=all_docs,
#         embedding=embeddings,
#         persist_directory="./biology_db",
#         collection_name="biology_grade9"
#     )
#     print(f"Done. {db._collection.count()} chunks stored.")

# else:
#     db = Chroma(
#         persist_directory="./biology_db",
#         embedding_function=embeddings,
#         collection_name="biology_grade9"
#     )
#     print(f"Loaded. {db._collection.count()} chunks.")

# def retrieve(query: str):

#     retriever = db.as_retriever(search_kwargs={"k": 20})
#     top20     = retriever.invoke(query)

#     passages  = [{"id": i, "text": doc.page_content, "meta": doc.metadata} for i, doc in enumerate(top20)]
#     request   = RerankRequest(query=query, passages=passages)
#     reranked  = ranker.rerank(request)[:5]

#     results = []
#     for p in reranked:
#      results.append({
#         "text": p["text"],
#         "metadata": p["meta"],
#         "score": round(p["score"], 4)
#     })
#     # result = retrieve("what is a bateria and fungi")
#     context = ""
#     for r in results:
#         context += r["text"] + "\n\n"
#     return context
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database.database import init_db
from routers.auth import router as auth_router


from fastapi.responses import FileResponse
from pydantic import BaseModel
# from ai.graph import app as rag_app
#from ai.lang import call_llm
from database.database import init_pools, close_pools, init_db
import sys
import os
from dotenv import load_dotenv
from routers.ai_conversation import router as conversation_router
load_dotenv()


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pools()   # open the pool
    await init_db()     # create tables if they don't exist
    yield
    await close_pools()  # shut the pool down cleanly when app stops
app = FastAPI(title="Student Assistant",
    swagger_ui_parameters={"persistAuthorization": True},
                           lifespan=lifespan)
app.include_router(auth_router)
app.include_router(conversation_router)

class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return FileResponse("ui/index.html")

# @app.post("/ask")
# def ask(query: Query):
#     result = call_llm(query.question)
#     return {"answer":result }

from langsmith import Client
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")

client = Client()
print("Connected:", client.list_projects())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
