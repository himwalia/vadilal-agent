import os
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory

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

def setup_retrieval_chain():
    """
    Set up the retrieval chain for the Vadilal AI chatbot.
    
    Returns:
        A conversational retrieval chain
    """
    # Get API key
    api_key = get_api_key()
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        model="openai/text-embedding-ada-002"
    )
    
    # Load the persisted database
    vectordb = Chroma(
        persist_directory="./vadilal_data_db",
        embedding_function=embeddings
    )
    
    # Initialize the retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    
    # Create a custom prompt template
    template = """
    You are a specialized AI assistant for the Vadilal Group, an Indian ice cream and frozen foods company.
    You have been trained on publicly available information about Vadilal Group.
    
    Your goal is to provide accurate, informative responses about:
    - Company overview, history, and structure
    - Financial performance and shareholding information
    - Product portfolio and market presence
    - Industry trends and competition
    - Leadership profiles and company updates
    
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer based on the provided context, just say that you don't have enough information - don't try to make up an answer.
    Keep your answers direct, professional, and informative.
    
    Context: {context}
    
    Question: {question}
    
    Helpful Answer:"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Initialize LLM with OpenRouter API
    llm = ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        model="anthropic/claude-3-sonnet@20240229",  # You can change to another model available on OpenRouter
        temperature=0.2,
        max_tokens=1000
    )
    
    # Create the conversational chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
    
    return chain

if __name__ == "__main__":
    # Example usage
    chain = setup_retrieval_chain()
    response = chain.invoke({"question": "What is Vadilal Group's main business?"})
    print(response["answer"])
