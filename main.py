from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from embeddings import get_embedding_function
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chroma"
DATA_PATH = BASE_DIR / "data" / "books"


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(
        str(DATA_PATH),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Split {len(documents)} docs into {len(chunks)} chunks")
    return chunks


def save_to_chroma(chunks: list[Document]):
    embedding_function = get_embedding_function()

    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)

    Chroma.from_documents(
        chunks,
        embedding_function,
        persist_directory=str(CHROMA_PATH),
    )

    print("Vector DB created!")


if __name__ == "__main__":
    main()
