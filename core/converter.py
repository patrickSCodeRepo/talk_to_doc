### Full PDF Vector Converter
import os
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings

# Expand user in file paths
path = os.path.expanduser('~/Ottoman.pdf')
# path = ""
save_dir = os.path.expanduser('./vectorstore/ottoman')

# Load the local PDF file if PDF

loader = PyPDFLoader(path)
docs_list = loader.load()
print(f"Loaded {len(docs_list)} documents.")


# Initialize embeddings
embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")

# Create Chroma vectorstore and persist to disk
vectorstore = Chroma.from_documents(
    documents=docs_list,
    embedding=embeddings,
    persist_directory=save_dir  # Specify the directory where Chroma will store data
)


__all__ = [name for name in globals() if not name.startswith('__')]