# test_embeddings.py
import os
import streamlit as st
from langchain_openai import OpenAIEmbeddings

def main():
    st.title("Testing OpenAIEmbeddings")
    
    # Get API key from secrets
    try:
        api_key = st.secrets["openrouter"]["api_key"]
    except:
        api_key = "test_key"  # For demonstration only
    
    st.write("Testing with minimal parameters...")
    try:
        # Most minimal initialization possible
        embeddings = OpenAIEmbeddings(
            api_key=api_key
        )
        st.success("Basic initialization works!")
    except Exception as e:
        st.error(f"Error with basic initialization: {str(e)}")
    
    st.write("Testing with OpenRouter parameters...")
    try:
        # Try with OpenRouter but minimal parameters
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        st.success("OpenRouter initialization works!")
    except Exception as e:
        st.error(f"Error with OpenRouter: {str(e)}")

if __name__ == "__main__":
    main()
