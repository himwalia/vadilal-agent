# check_versions.py
import streamlit as st
import pkg_resources

def main():
    st.title("Package Versions")
    
    packages = [
        "langchain", 
        "langchain-openai",
        "langchain-community",
        "openai"
    ]
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            st.write(f"{package}: {version}")
        except:
            st.write(f"{package}: Not installed")

if __name__ == "__main__":
    main()
