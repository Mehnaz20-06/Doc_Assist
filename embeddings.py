from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_function():
    try:
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"local_files_only": True},
        )
    except Exception:
        print("Local embedding model not found; downloading from Hugging Face...")
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
