from ai.llm import llm
def build_retrieval_query(query: str, history: list[dict]) -> str:
    if not history:
        return query
    
    # take last 2 exchanges only, enough context for retrieval
    recent = history[-6:]
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
    
    return f"{history_text}\nhuman: {query}"
def summarize_history(history: list[dict]) -> str:
    if not history:
        return ""
    
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history
    )
    
    summary = llm.invoke(
        f"Summarize this conversation briefly in 2-3 lines:\n{history_text}"
    )
    
    return summary.content