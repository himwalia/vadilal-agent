import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_vadilal_data(file_path):
    """
    Process the Vadilal Group text data and store it in a vector database.
    
    Args:
        file_path: Path to the text file containing Vadilal data
    
    Returns:
        A Chroma vector database instance
    """
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
    
    # Create embeddings using OpenRouter API (with OpenAI compatible endpoint)
    print("Creating embeddings...")
    # Use your OpenRouter API key with OpenAI-compatible embedding model
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        model="openai/text-embedding-ada-002"  # Use an embedding model available on OpenRouter
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
