import streamlit as st
import requests
import json

def main():
    st.title("🍦 Vadilal Group AI Assistant")
    
    # Try to get API key from secrets
    try:
        api_key = st.secrets["openrouter"]["api_key"]
    except:
        api_key = None
        st.error("API key not found in secrets. Please add it to Streamlit secrets.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Vadilal Group AI assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Get user input
    if user_input := st.chat_input("Ask something about Vadilal Group..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Display assistant response
        with st.chat_message("assistant"):
            if api_key:
                with st.spinner("Thinking..."):
                    # Call OpenRouter API directly
                    response = call_openrouter(user_input, api_key)
                    st.write(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.write("Please add your OpenRouter API key to Streamlit secrets.")

    # Add sample questions in sidebar
    st.sidebar.title("Sample Questions")
    sample_questions = [
        "What is the shareholding breakdown of Vadilal Group?",
        "Who are the biggest direct competitors of the company?",
        "What has been the historical financial performance over the last 3 financial years?",
        "What are the key trends driving the Indian ice cream industry in 2025?",
        "Who are the key leaders in Vadilal Group?",
        "What is Vadilal's market share in the Indian ice cream industry?"
    ]
    
    for question in sample_questions:
        if st.sidebar.button(question):
            # Set the question in the chat input
            # This is a hack since we can't directly set the chat input value
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            
            with st.chat_message("assistant"):
                if api_key:
                    with st.spinner("Thinking..."):
                        response = call_openrouter(question, api_key)
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.write("Please add your OpenRouter API key to Streamlit secrets.")
            
            # Force a rerun to update the UI
            st.experimental_rerun()

def call_openrouter(prompt, api_key):
    """Call OpenRouter API directly without using langchain."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://vadilal-chat-agent.streamlit.app/", 
        "X-Title": "Vadilal Group AI Assistant",
        "Content-Type": "application/json"
    }
    
    # Prepare system message with Vadilal context
    system_message = """You are a specialized AI assistant for the Vadilal Group, an Indian ice cream and frozen foods company.

Key facts about Vadilal:
- Founded in 1907, Vadilal is one of the oldest ice cream brands in India
- It offers over 150 ice cream products across various segments
- Major competitors include Amul, Kwality Walls, Mother Dairy, and Havmor
- The company has a strong presence in exports, especially to the USA, UK, and Middle East
- Vadilal Industries Ltd. and Vadilal Enterprises Ltd. are the main public companies
- They also have businesses in processed foods, dairy products, and quick service restaurants

Your goal is to provide accurate, helpful information about Vadilal's business, products, history, financial performance, market position, and industry trends based on publicly available information.

If you don't know the answer to a specific question, acknowledge that and provide related general information that might be helpful."""

    # Prepare conversation history (only include the last several messages)
    messages = [{"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages[-6:] if m["role"] in ["user", "assistant"]]
    
    # Add system message
    messages.insert(0, {"role": "system", "content": system_message})
    
    data = {
        "model": "anthropic/claude-3-sonnet@20240229",  # Using Claude Sonnet as fallback
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            return f"Error: I'm having trouble connecting to the AI model. Please try again later."
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: Something went wrong. Please try again later."

if __name__ == "__main__":
    main()
