import streamlit as st
import requests
import json

def main():
    st.title("Vadilal Group AI Assistant")
    
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

def call_openrouter(prompt, api_key):
    """Call OpenRouter API directly without using langchain."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://vadilal-chat-agent.streamlit.app/", # Required by OpenRouter
        "X-Title": "Vadilal Group AI Assistant",  # Optional but recommended
        "Content-Type": "application/json"
    }
    
    # Prepare conversation history (only include the last few messages to keep context concise)
    messages = [{"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages[-5:] if m["role"] in ["user", "assistant"]]
    
    # Add system message
    messages.insert(0, {
        "role": "system", 
        "content": """You are a specialized AI assistant for the Vadilal Group, an Indian ice cream and frozen foods company.
        Your goal is to provide accurate, informative responses about the company's history, products, financials, 
        and market presence based on publicly available information."""
    })
    
    data = {
        "model": "meta/llama-4-maverick",  # Use Llama 4 Maverick
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # Debug information
        st.write(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            st.write(f"Response: {response.text}")
            return f"Error: {response.status_code} - {response.text}"
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    main()
