import argparse
from pathlib import Path

import requests
from embeddings import get_embedding_function
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chroma"
OLLAMA_MODEL = "phi3:mini"
OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_TEMPLATE = """
Answer ONLY from the context below.

Context:
{context}

---

Question: {question}
Answer:
"""


def answer_query(query_text: str):
    embedding_function = get_embedding_function()

    db = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embedding_function,
    )

    results = db.similarity_search(query_text, k=3)

    if not results:
        return "No results found"

    context_text = "\n\n---\n\n".join(
        [doc.page_content for doc in results]
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context_text,
        question=query_text,
    )

    try:
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 1024,
                },
            },
            timeout=120,
        )
        ollama_response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return "Could not connect to Ollama. Start Ollama, then run this command again."
    except requests.exceptions.HTTPError as error:
        return f"Ollama returned an error: {error}\nResponse: {ollama_response.text}"

    return ollama_response.json()["response"].strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str)
    args = parser.parse_args()

    response = answer_query(args.query_text)

    print("\nAnswer:\n", response)


if __name__ == "__main__":
    main()
