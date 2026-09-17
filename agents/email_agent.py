from typing import Dict, Any

from langchain_groq import ChatGroq

from tools.email_tools import get_email_thread
from tools.retriever import EmailThreadRetriever


class EmailAgent:

    def __init__(self, model: ChatGroq):
        self.model = model
        self.retriever = EmailThreadRetriever()

    def search(self, query: str) -> Dict[str, Any]:

        results = self.retriever.search(
            query=query,
            top_k=3
        )

        return {
            "query": query,
            "source": "email",
            "results": results
        }

    def get_thread(self, thread_id: str) -> Dict[str, Any]:

        thread = get_email_thread(thread_id)

        return {
            "thread_id": thread_id,
            "source": "email",
            "thread": thread
        }