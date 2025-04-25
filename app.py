import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import setup_retrieval_chain
from data_processing import process_vadilal_data

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Vadilal Group AI Assistant",
    page_icon="🍦",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #e6f7ff;
    }
    .chat-message.bot {
        background-color: #f0f2f5;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .chat-message .user-avatar {
        background-color: #2b7bf7;
        color: white;
    }
    .chat-message .bot-avatar {
        background-color: #0f52ba;
        color: white;
    }
    .chat-message .message {
        flex-grow: 1;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'chain' not in st.session_state:
        try:
            st.session_state.chain = setup_retrieval_chain()
        except Exception as e:
            st.error(f"Error initializing RAG system: {str(e)}")
            st.session_state.chain = None

def display_messages():
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.container():
                st.markdown(f"""
                <div class="chat-message user">
                    <div class="avatar user-avatar">👤</div>
                    <div class="message">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown(f"""
                <div class="chat-message bot">
                    <div class="avatar bot-avatar">🍦</div>
                    <div class="message">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

def process_user_input():
    if user_query := st.chat_input("Ask something about Vadilal Group..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Display loading spinner while processing
        with st.spinner("Thinking..."):
            if st.session_state.chain:
                try:
                    # Get response from the chain
                    response = st.session_state.chain.invoke({"question": user_query})
                    answer = response["answer"]
                except Exception as e:
                    answer = f"I encountered an error while processing your question: {str(e)}"
            else:
                answer = "I'm having trouble accessing the Vadilal Group information. Please check the system setup."
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

def upload_data_file():
    uploaded_file = st.file_uploader("Upload your Vadilal data text file", type=["txt"])
    if uploaded_file is not None:
        # Save the uploaded file
        with open("vadilal_data.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("File uploaded successfully! Processing data...")
        
        # Process the data
        with st.spinner("Processing Vadilal data... This may take a few minutes."):
            try:
                process_vadilal_data("vadilal_data.txt")
                st.success("Data processed successfully! The AI assistant is ready to use.")
                
                # Reinitialize the chain
                st.session_state.chain = setup_retrieval_chain()
                
                # Add a welcome message
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Hello! I'm your Vadilal Group AI assistant. How can I help you today?"
                    })
                
                # Rerun to refresh the page
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

def main():
    # Display header
    st.title("🍦 Vadilal Group AI Assistant")
    st.markdown("""
    Welcome to the Vadilal Group AI Assistant. I can help you with information about:
    - Company overview and history
    - Financial performance
    - Shareholding breakdown
    - Competitors analysis
    - Industry trends
    - Products and services
    - Leadership profiles
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Check if data is already loaded
    if not os.path.exists("./vadilal_data_db"):
        st.warning("No Vadilal data found. Please upload your data file to get started.")
        upload_data_file()
    else:
        # Display chat messages
        display_messages()
        
        # Get user input
        process_user_input()
        
        # Add option to upload new data
        with st.sidebar:
            st.header("Update Data")
            st.write("If you want to update the Vadilal Group data, upload a new file:")
            upload_data_file()
            
            # Add sample questions
            st.header("Sample Questions")
            sample_questions = [
                "What is the shareholding breakdown of Vadilal Group?",
                "Who are the biggest direct competitors of the company?",
                "What has been the historical financial performance over the last 3 financial years?",
                "What are the key trends driving the Indian ice cream industry in 2025?",
                "Who are the key leaders in Vadilal Group?",
                "What is Vadilal's market share in the Indian ice cream industry?"
            ]
            
            for question in sample_questions:
                if st.button(question):
                    # Add the sample question to the messages
                    st.session_state.messages.append({"role": "user", "content": question})
                    
                    # Get response from the chain
                    with st.spinner("Thinking..."):
                        if st.session_state.chain:
                            try:
                                response = st.session_state.chain.invoke({"question": question})
                                answer = response["answer"]
                            except Exception as e:
                                answer = f"I encountered an error while processing your question: {str(e)}"
                        else:
                            answer = "I'm having trouble accessing the Vadilal Group information. Please check the system setup."
                    
                    # Add the response to the messages
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Rerun to update the UI
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
