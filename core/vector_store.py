import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import settings

# Initialize Embeddings
embeddings = OllamaEmbeddings(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL
)

# Initialize ChromaDB
# Persist data to ./chroma_db directory to keep it across restarts
persist_directory = "./chroma_db"

vector_store = Chroma(
    collection_name="pharma_clinical_data",
    embedding_function=embeddings,
    persist_directory=persist_directory
)

# For compatibility with previous usage, we expose the vector store instance
# The 'index' concept works differently in Chroma (it's a collection), 
# but we will adapt the calling code (tools) to use vector_store.similarity_search
