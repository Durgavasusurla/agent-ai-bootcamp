"""RAG assistant with metrics (course lessons 02, 04, 05), Groq client."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from ingest import load_faq_data, build_index
from metrics import RAGWithMetrics

# keys live in the project root .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def groq_client():
    # Course: OpenAI()
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )


def create_assistant():
    documents = load_faq_data()
    index = build_index(documents)

    return RAGWithMetrics(
        index=index,
        llm_client=groq_client(),
    )


if __name__ == "__main__":
    from db_save import save_conversation

    assistant = create_assistant()

    query = "How do I join the course?"
    if len(sys.argv) > 1:
        query = sys.argv[1]

    answer = assistant.rag(query)
    print(answer)

    conversation_id = save_conversation(assistant.last_call, query, "llm-zoomcamp")
    print(f"saved conversation {conversation_id}")
