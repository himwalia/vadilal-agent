import streamlit as st
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

def test_embeddings():
    st.subheader("Testing OpenAI Embeddings")
    
    # Get API key from secrets
    try:
        api_key = st.secrets["openrouter"]["api_key"]
        st.success("Successfully retrieved API key from secrets")
    except Exception as e:
        st.error(f"Error retrieving API key: {str(e)}")
        return
    
    # Test embeddings with minimal parameters
    st.write("Testing embeddings with minimal parameters...")
    try:
        embeddings = OpenAIEmbeddings(api_key=api_key)
        result = embeddings.embed_query("Test query")
        st.success(f"✅ Basic embeddings work! Vector length: {len(result)}")
    except Exception as e:
        st.error(f"❌ Basic embeddings failed: {str(e)}")
    
    # Test with OpenRouter parameters
    st.write("Testing embeddings with OpenRouter...")
    try:
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/text-embedding-ada-002"
        )
        result = embeddings.embed_query("Vadilal ice cream")
        st.success(f"✅ OpenRouter embeddings work! Vector length: {len(result)}")
    except Exception as e:
        st.error(f"❌ OpenRouter embeddings failed: {str(e)}")

def test_chat_completion():
    st.subheader("Testing Chat Completion")
    
    # Get API key from secrets
    try:
        api_key = st.secrets["openrouter"]["api_key"]
    except Exception as e:
        st.error(f"Error retrieving API key: {str(e)}")
        return
    
    # Test chat completion
    st.write("Testing chat completion with Llama 4...")
    try:
        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="meta/llama-4-maverick"
        )
        result = llm.invoke("Tell me briefly about Vadilal ice cream")
        st.success("✅ Chat completion works!")
        st.write("Response:")
        st.write(result.content)
    except Exception as e:
        st.error(f"❌ Chat completion failed: {str(e)}")

def main():
    st.title("Vadilal Assistant - Diagnostic")
    
    st.write("""
    This page tests core functionality to diagnose issues with the Vadilal assistant.
    Click the buttons below to test different components.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Embeddings"):
            test_embeddings()
    
    with col2:
        if st.button("Test Chat Completion"):
            test_chat_completion()
    
    st.divider()
    
    # Simple question answering
    st.subheader("Simple Question Answering")
    user_input = st.text_input("Ask a question about Vadilal:")
    if user_input:
        st.write(f"You asked: {user_input}")
        st.write("This is a placeholder response while we fix the RAG system.")

if __name__ == "__main__":
    main()
