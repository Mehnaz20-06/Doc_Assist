# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is a technique that enhances Large Language Models (LLMs) by combining them with external knowledge sources.

## How RAG Works

1. Documents are split into smaller chunks.
2. Each chunk is converted into embeddings (vector representation).
3. Embeddings are stored in a vector database.
4. When a user asks a query:
   - The query is converted into an embedding.
   - Similar chunks are retrieved.
   - Retrieved context is passed to the LLM.
   - The LLM generates a response using this context.

## Key Components

- Embeddings
- Vector Database (e.g., Chroma, FAISS)
- Retriever
- Generator (LLM)

## Advantages

- Reduces hallucination
- Uses up-to-date knowledge
- Works without retraining the model

## Example Use Cases

- Chatbots for documents
- Knowledge assistants
- Customer support systems