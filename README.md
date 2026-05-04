# Doc_Assist
# AI For Docs - Local RAG Q&A System

This project is a simple local Retrieval-Augmented Generation (RAG) app. It allows users to upload Markdown documents, convert them into a vector database, and ask questions from those documents using a local LLM through Ollama.

## How It Works

The project follows this flow:

1. Markdown files are stored inside `data/books`.
2. `main.py` loads all `.md` files.
3. The documents are split into smaller chunks.
4. Each chunk is converted into embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
5. The embeddings are stored in a local Chroma vector database.
6. When the user asks a question, `query_data.py` searches Chroma for the most relevant chunks.
7. The retrieved context is sent to Ollama running `phi3:mini`.
8. The LLM generates an answer using only the retrieved document context.
9. python app.py on powershell then open http://127.0.0.1:5000

**Technologies Used**
Python
LangChain
ChromaDB
Hugging Face sentence-transformers
Ollama
phi3:mini
Flask
HTML/CSS
