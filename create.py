import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Ensure the OpenAI API key is set
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Ensure the docs path is set
if "DOCS_PATH" not in os.environ:
    raise ValueError("Please set the DOCS_PATH environment variable")

docs_path = os.environ["DOCS_PATH"]

# Initialize the OpenAI embeddings
embedding = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"], model="text-embedding-3-large")

# Manually traverse the directory and collect all relevant files
file_paths = []
for ext in ["**/*.md", "**/*.py", "**/*.rst"]:
    file_paths.extend(glob.glob(os.path.join(docs_path, ext), recursive=True))

# Create a loader to process text files
documents = []
for file_path in file_paths:
    print(f"Loading document: {file_path}")
    loader = TextLoader(file_path)
    documents.extend(loader.load())

# Check if documents are empty
if not documents:
    print("No documents found. Please check the path and file extensions.")
else:
    # Split documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    # Create a vector database using Chroma
    vectordb = Chroma(persist_directory="my_db", embedding_function=embedding)

    # Print and add split documents to the vector database
    print("Split documents:")
    for doc in docs:
        print("Adding document from file:", doc.metadata["source"])
        vectordb.add_documents([doc])

    print("Embedding created and saved successfully.")
