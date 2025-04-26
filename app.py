import streamlit as st
import requests
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Vadilal AI Assistant",
    page_icon="🍦",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066b2;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    .user-message {
        background-color: #e6f2ff;
        border-left: 5px solid #0066b2;
    }
    .assistant-message {
        background-color: #f0f0f0;
        border-left: 5px solid #F48024;
    }
    .message-content {
        margin-left: 1rem;
    }
    .vadilal-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Load Vadilal data from file
def load_vadilal_data():
    try:
        with open("vadilal_data.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        # Fallback data if file is not found
        return """
        Vadilal Group - Company Information:

        Founded: 1907 by Vadilal Gandhi
        Headquarters: Ahmedabad, Gujarat, India
        Industry: Ice Cream and Frozen Desserts Manufacturing

        Key Products:
        - Ice creams (150+ flavors and varieties)
        - Frozen desserts
        - Frozen vegetables
        - Processed foods
        - Ready-to-eat snacks

        Market Position:
        - Second largest ice cream brand in India
        - Exports to USA, UK, UAE, Canada, Australia, New Zealand, and several African and Southeast Asian countries
        - Operates two major manufacturing facilities in India (Pundhra in Gujarat and Bareilly in Uttar Pradesh)

        Financial Information (as of FY 2023-24):
        - Annual turnover: Approximately INR 900+ crore (USD 110+ million)
        - Listed on BSE and NSE
        - Stock symbols: VADILALIND (BSE) and VADILALIND (NSE)

        Key Competitors:
        - Amul (Gujarat Cooperative Milk Marketing Federation)
        - Hindustan Unilever (Kwality Wall's)
        - Mother Dairy
        - Havmor
        - Baskin Robbins
        - Natural Ice Cream
        """

# Load API key from environment or secrets
def get_api_key():
    # First try to get from Streamlit secrets
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except:
        # Then try environment variable
        return os.environ.get("OPENROUTER_API_KEY", "")

# Constants and configuration
OPENROUTER_API_KEY = get_api_key()
VADILAL_DATA = load_vadilal_data()
DEFAULT_MODEL = "meta-llama/llama-4-maverick:free"

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to call the LLM API (OpenRouter)
def query_llm(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare messages with context
    system_message = f"""You are a helpful AI assistant for Vadilal Group, an Indian ice cream company. 
    Answer questions based on the following information about Vadilal. 
    If you don't know the answer, politely say so without making up information.
    
    VADILAL INFORMATION:
    {VADILAL_DATA}
    
    Current date: {datetime.now().strftime('%B %d, %Y')}
    """
    
    messages = [
        {"role": "system", "content": system_message},
    ]
    
    # Add conversation history (limited to last 10 messages to save tokens)
    for message in st.session_state.messages[-10:]:
        messages.append({"role": message["role"], "content": message["content"]})
    
    # Add current prompt
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Error: Unexpected response format from API"
    except requests.exceptions.RequestException as e:
        # Improved error handling with specific details
        error_msg = f"API Error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                error_msg = "Error 400: Bad request. Check API parameters."
            elif e.response.status_code == 401:
                error_msg = "Error 401: Authentication failed. API key issue."
            elif e.response.status_code == 429:
                error_msg = "Error 429: Too many requests. Please try again later."
            
            # Try to get more details from response
            try:
                response_json = e.response.json()
                if "error" in response_json and "message" in response_json["error"]:
                    error_msg += f"\nDetails: {response_json['error']['message']}"
            except:
                pass
        
        return f"{error_msg}"

# Check if API key is available
def is_api_configured():
    return bool(OPENROUTER_API_KEY)

# Main app interface
st.markdown('<div class="vadilal-logo"><h1 class="main-header">🍦 Vadilal AI Assistant</h1></div>', unsafe_allow_html=True)

# Add sidebar for app info and controls
with st.sidebar:
    st.header("About")
    st.write("This AI assistant provides information about Vadilal Group using publicly available data.")
    
    # Show model info
    st.subheader("Model Information")
    st.write(f"Using: Llama 4 Maverick")
    
    # API status indicator
    st.subheader("API Status")
    if is_api_configured():
        st.success("API key configured ✓")
    else:
        st.error("API key not found! Please set OPENROUTER_API_KEY in environment variables or Streamlit secrets.")
    
    # Add clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">👤 <div class="message-content">{message["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">🍦 <div class="message-content">{message["content"]}</div></div>', unsafe_allow_html=True)

# Chat input
with st.container():
    user_input = st.chat_input("Ask me about Vadilal...")
    
    if user_input:
        # Display user message
        st.markdown(f'<div class="chat-message user-message">👤 <div class="message-content">{user_input}</div></div>', unsafe_allow_html=True)
        
        # Save to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Check if API is configured
        if not is_api_configured():
            response = "⚠️ API key is not configured. Please set OPENROUTER_API_KEY in environment variables or Streamlit secrets."
        else:
            # Get response from API
            with st.spinner('Thinking...'):
                response = query_llm(user_input)
        
        # Display assistant response
        st.markdown(f'<div class="chat-message assistant-message">🍦 <div class="message-content">{response}</div></div>', unsafe_allow_html=True)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown('<div class="footer">Vadilal AI Assistant - Using publicly available information only</div>', unsafe_allow_html=True)
