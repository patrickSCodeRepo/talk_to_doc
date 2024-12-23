import streamlit as st
import time

st.write("### Drop files below for conversion")
path = st.file_uploader("# Please upload your file below", type="pdf")


### Full PDF Vector Converter
import os
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings

# Expand user in file paths
pdf_path = os.path.expanduser('~/Ottoman.pdf')
save_dir = os.path.expanduser('./ottoman_vectorstore')

# Load the local PDF file if PDF

loader = PyPDFLoader(pdf_path)
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
