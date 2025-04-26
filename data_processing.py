import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def get_api_key():
    # Try to get API key from Streamlit secrets first (for production)
    try:
        return st.secrets["openrouter"]["api_key"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variable (for local development)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            st.error("OpenRouter API key not found. Please add it to your Streamlit secrets or .env file.")
        return api_key

def process_vadilal_data(file_path):
    """
    Process the Vadilal Group text data and store it in a vector database.
    
    Args:
        file_path: Path to the text file containing Vadilal data
    
    Returns:
        A Chroma vector database instance
    """
    # Get API key
    api_key = get_api_key()
    
    # Read the data file
    print(f"Reading data from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        vadilal_data = file.read()
    
    # Split text into chunks
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(vadilal_data)
    print(f"Created {len(chunks)} chunks of text")
    
    # Create ChatOpenAIusing OpenRouter API (with OpenAI compatible endpoint)
    print("Creating embeddings...")
    ChatOpenAI= OpenAIEmbeddings(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model="openai/text-embedding-ada-002",
        # Remove any proxies parameter if it exists
    )
    
    # Create and persist vector store
    print("Creating vector database...")
    db = Chroma.from_texts(
        chunks, 
        embeddings, 
        persist_directory="./vadilal_data_db"
    )
    
    print("Vector database created successfully!")
    return db

if __name__ == "__main__":
    # Example usage
    db = process_vadilal_data("vadilal_data.txt")
    db.persist()
    print("Database persisted to disk. Ready for querying!")
