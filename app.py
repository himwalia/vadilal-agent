import streamlit as st

def main():
    st.title("Simplified Vadilal Assistant")
    st.write("This is a simplified version to test deployment.")
    
    # Display some basic UI
    st.write("Welcome to the Vadilal Group AI Assistant!")
    
    # Add a basic input
    user_input = st.text_input("Ask a question:")
    if user_input:
        st.write(f"You asked: {user_input}")
        st.write("This is a placeholder response while we fix the embedding issues.")

if __name__ == "__main__":
    main()
