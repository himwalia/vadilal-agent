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

# Vadilal company data (publicly available)
VADILAL_DATA = """
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

Recent Developments:
- Expanded export markets to include new countries in Africa and Southeast Asia
- Launched premium product lines targeting the luxury ice cream segment
- Increased focus on healthy and natural ingredient-based products
- Modernized manufacturing facilities with state-of-the-art equipment
- Invested in cold chain infrastructure to improve distribution
- Adapted to post-COVID market changes with increased home delivery options

Corporate Structure:
- Vadilal Industries Limited (publicly listed company)
- Vadilal Enterprises Limited (distribution arm)
- Vadilal International Private Limited (export business)
- Family-owned business with professional management

Industry Trends:
- Growing preference for natural and healthier ice cream options
- Premium and specialty ice cream segments showing strong growth
- Increased competition from both organized and unorganized sectors
- Seasonal demand variations with peak sales during summer months
- Expansion of cold chain infrastructure across India improving market reach
- Rising disposable incomes driving growth in ice cream consumption
- Increasing urbanization and changing food habits benefiting packaged ice cream sales
"""

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to call the LLM API (OpenRouter)
def query_llm(prompt, openrouter_api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
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
    
    # Add conversation history
    for message in st.session_state.messages:
        messages.append({"role": message["role"], "content": message["content"]})
    
    # Add current prompt
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "anthropic/claude-3-haiku", # Can be changed to other models
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()  # Raise exception for 4XX/5XX errors
        
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
                error_msg = "Error 400: Bad request. Please check your API key and parameters."
            elif e.response.status_code == 401:
                error_msg = "Error 401: Authentication failed. Please check your API key."
            elif e.response.status_code == 429:
                error_msg = "Error 429: Too many requests. Please try again later."
            
            # Try to get more details from response
            try:
                response_json = e.response.json()
                if "error" in response_json and "message" in response_json["error"]:
                    error_msg += f"\nDetails: {response_json['error']['message']}"
            except:
                pass
        
        return f"{error_msg}\n\nTry an alternative approach: check your API connection settings or try a different LLM provider."

# Alternative function using direct Anthropic API (in case OpenRouter continues to fail)
def query_anthropic(prompt, anthropic_api_key):
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    system_message = f"""You are a helpful AI assistant for Vadilal Group, an Indian ice cream company. 
    Answer questions based on the following information about Vadilal. 
    If you don't know the answer, politely say so without making up information.
    
    VADILAL INFORMATION:
    {VADILAL_DATA}
    
    Current date: {datetime.now().strftime('%B %d, %Y')}
    """
    
    # Format history in Anthropic's format
    messages = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            messages.append({"role": "user", "content": message["content"]})
        else:
            messages.append({"role": "assistant", "content": message["content"]})
    
    # Add current prompt
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "claude-3-haiku-20240307",
        "system": system_message,
        "messages": messages,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if "content" in result and len(result["content"]) > 0:
            return result["content"][0]["text"]
        else:
            return "Error: Unexpected response format from API"
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Main app interface
st.markdown('<div class="vadilal-logo"><h1 class="main-header">🍦 Vadilal AI Assistant</h1></div>', unsafe_allow_html=True)

# Sidebar for API key input
with st.sidebar:
    st.header("API Configuration")
    api_option = st.radio("Select API Provider:", ["OpenRouter", "Anthropic Direct"])
    
    if api_option == "OpenRouter":
        api_key = st.text_input("OpenRouter API Key", type="password", 
                               help="Enter your OpenRouter API key. Keep it confidential.")
    else:
        api_key = st.text_input("Anthropic API Key", type="password", 
                               help="Enter your Anthropic API key. Keep it confidential.")
    
    # Model selection based on provider
    if api_option == "OpenRouter":
        model_options = {
            "Claude 3 Haiku": "anthropic/claude-3-haiku",
            "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
            "Claude 3 Opus": "anthropic/claude-3-opus",
            "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
            "Llama 3 70B": "meta-llama/llama-3-70b-instruct"
        }
    else:
        model_options = {
            "Claude 3 Haiku": "claude-3-haiku-20240307",
            "Claude 3 Sonnet": "claude-3-sonnet-20240229",
            "Claude 3 Opus": "claude-3-opus-20240229"
        }
    
    selected_model = st.selectbox("Select Model:", list(model_options.keys()))
    
    st.divider()
    st.subheader("About")
    st.write("This AI assistant provides information about Vadilal Group using publicly available data.")
    
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
        
        # Get response from selected API
        with st.spinner('Thinking...'):
            if api_key:
                if api_option == "OpenRouter":
                    response = query_llm(user_input, api_key)
                else:
                    response = query_anthropic(user_input, api_key)
            else:
                response = "⚠️ Please enter an API key in the sidebar to continue."
        
        # Display assistant response
        st.markdown(f'<div class="chat-message assistant-message">🍦 <div class="message-content">{response}</div></div>', unsafe_allow_html=True)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown('<div class="footer">Vadilal AI Assistant - Using publicly available information only</div>', unsafe_allow_html=True)
