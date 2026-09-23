import json
import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.embeddings import OllamaEmbeddings
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
#from sentence_transformers import CrossEncoder
from flashrank import Ranker, RerankRequest
import sys
sys.path.insert(0, r"D:\AI engineering\AI_FOR_RURAL\G_9 biology")

embeddings = OllamaEmbeddings(model="nomic-embed-text")
# reranker   = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
def chunk_splitter():
   pages = []
   with pdfplumber.open("books/Biology_9.pdf") as pdf:
           for i, page in enumerate(pdf.pages):
               text = page.extract_text()
               if text and text.strip():
                   pages.append(Document(
                       page_content=text,
                       metadata={"page": i + 1, "type": "text"}
                   ))
   
   splitter = RecursiveCharacterTextSplitter(
           chunk_size=1000,
           chunk_overlap=100
       ) 
   text_docs = splitter.split_documents(pages)
   return text_docs
    
if not os.path.exists("./biology_db") or not os.listdir("./biology_db"):

    
    text_docs = chunk_splitter()

    with open("chart_annotations.json") as f:
        charts = json.load(f)
    with open("table_summaries.json") as f:
        tables = json.load(f)

    json_docs = []
    for entry in charts + tables:
        json_docs.append(Document(
            page_content=entry["description"],
            metadata={
                "id":      entry["id"],
                "page":    entry["page"],
                "type":    entry["type"],
                "topic":   entry["topic"],
                "chapter": entry["chapter"],
                "grade":   entry["grade"],
                "subject": entry["subject"]
            }
        ))

    all_docs = text_docs + json_docs

    db = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory="./biology_db",
        collection_name="biology_grade9"
    )
    print(f"Done. {db._collection.count()} chunks stored.")

else:
    db = Chroma(
        persist_directory="./biology_db",
        embedding_function=embeddings,
        collection_name="biology_grade9"
    )
    print(f"Loaded. {db._collection.count()} chunks.")


    
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(chunk_splitter())
bm25_retriever.k = 7
vector_retriever = db.as_retriever(search_kwargs={"k": 7})
#print(bm25_retriever.invoke("what is osmosis and diffusion"))

import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("groq_api_key")
llm = ChatGroq(api_key=groq_api_key,
               model="openai/gpt-oss-20b", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the user query into 3 specific sub-queries for document retrieval. Return only a numbered list, nothing else."),
    ("human", "{query}")
])

def transform_and_retrieve(query: str) -> list:
    # Step 1: transform
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"query": query})
    #print(result)
    lines = [line.strip() for line in result.strip().split("\n") if line.strip()]
    sub_queries = [line.split(". ", 1)[-1] for line in lines if line[0].isdigit()]
    # return sub_queries
    ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)
    all_chunks = []
    for sub_query in sub_queries:
        chunks = ensemble_retriever.invoke(sub_query)  # returns ~7 chunks
        all_chunks.extend(chunks)
    
    
    seen = set()
    unique_chunks = []
    for chunk in all_chunks:
        if chunk.page_content not in seen:
            seen.add(chunk.page_content)
            unique_chunks.append(chunk)
    
    return unique_chunks  # ~20 chunks → ready for reranking


def reranked(query, top20):
    
    passages  = [{"id": i, "text": doc.page_content, "meta": doc.metadata} for i, doc in enumerate(top20)]
    request   = RerankRequest(query=query, passages=passages)
    reranked  = ranker.rerank(request)[:5]

    results = []
    for p in reranked:
     results.append({
        "text": p["text"],
        "metadata": p["meta"],
        "score": round(p["score"], 4)
    })
    # result = retrieve("what is a bateria and fungi")
    context = ""
    for r in results:
        context += r["text"] + "\n\n"
    return context
def final_chunk(query):
  top20 = transform_and_retrieve(query)
  reranked_result= reranked(query, top20)
  return reranked_result 
# query = "this osmosis thing and diffusion is complicated what even is it?"
# results = transform_and_retrieve(query)
# reranked_result = reranked(results)

#print(results)
# print(reranked_result)
# print(len(reranked_result))
# from langsmith import Client
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
# os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")

# client = Client()
# print("Connected:", client.list_projects())