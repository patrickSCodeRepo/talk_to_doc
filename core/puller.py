### Pull documents from the Chroma DB
import os
from langchain_chroma import Chroma
from langchain_nomic.embeddings import NomicEmbeddings

# Get vectorstore file directory
rag_app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
save_dir = os.path.join(rag_app_dir, 'ottoman_vectorstore')

# Initialize embeddings
embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")

# Load the vectorstore from disk
vectorstore = Chroma(
    persist_directory=save_dir,
    embedding_function=embeddings
)

# Retrieve all documents from the vector store
docs = vectorstore.get()

# Create retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})