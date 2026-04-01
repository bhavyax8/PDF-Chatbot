import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"[Ingestion] Loaded {len(documents)} pages from PDF.")

    splitter  = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators = ["\n\n", "\n", ".", ""])
    chunks = splitter.split_documents(documents)
    print(f"[Ingestion] Split into {len(chunks)} chunks.")
    return chunks
