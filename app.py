import streamlit as st
import re
import nltk
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Page configuration
st.set_page_config(
    page_title="Vadilal Group AI Agent",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main-header {color: #0066b2; font-size: 2.5em;}
    .sub-header {color: #0066b2; font-size: 1.5em;}
    .stButton button {background-color: #0066b2; color: white;}
    .info-box {background-color: #f0f8ff; padding: 20px; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">Vadilal Group Knowledge Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
Ask any questions about Vadilal Group's business, financial performance, competitors, market position, and the ice cream industry in India.
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'chunks' not in st.session_state:
    st.session_state.chunks = []
    st.session_state.tfidf_matrix = None
    st.session_state.vectorizer = None

# Load and prepare data
@st.cache_resource
def load_and_process_data():
    # Load the document
    with open("vadilal_deepsearch.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Extract sections
    sections = re.split(r'\*\*\d+\.\s+[A-Z\s]+(\([^)]+\))?\*\*|\*\*[A-Z\s]+(:|)\*\*', text)
    
    # Process sections into chunks
    chunks = []
    chunk_id = 0
    
    # First pass: create larger contextual chunks based on sections
    for section in sections:
        if len(section.strip()) > 100:  # Ignore small sections which might be just titles
            paragraphs = re.split(r'\n\n+', section)
            for para in paragraphs:
                if len(para.strip()) > 100:  # Only include substantial paragraphs
                    # Determine section type
                    section_type = "General"
                    if "COMPANY OVERVIEW" in para or "Manufacturing Facilities" in para:
                        section_type = "Company Overview"
                    elif "FINANCIAL PERFORMANCE" in para or "Annual Revenue" in para:
                        section_type = "Financial Performance"
                    elif "SHAREHOLDING" in para or "Promoter Holding" in para:
                        section_type = "Shareholding"
                    elif "COMPETITOR" in para or "Market Share" in para:
                        section_type = "Competitors"
                    elif "INDUSTRY TRENDS" in para or "Market Size" in para:
                        section_type = "Industry Trends"
                    
                    chunks.append({
                        "id": chunk_id,
                        "text": para,
                        "section": section_type
                    })
                    chunk_id += 1
    
    # Create TF-IDF vectorizer and fit on all chunks
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([chunk["text"] for chunk in chunks])
    
    return chunks, tfidf_matrix, vectorizer

# Search function using TF-IDF and cosine similarity
def search_relevant_chunks(query, top_k=5):
    # Transform the query using the fitted vectorizer
    query_vector = st.session_state.vectorizer.transform([query])
    
    # Calculate cosine similarity between query and all chunks
    similarities = cosine_similarity(query_vector, st.session_state.tfidf_matrix).flatten()
    
    # Get indices of top k similar chunks
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # Return the chunks corresponding to these indices
    return [st.session_state.chunks[i] for i in top_indices if similarities[i] > 0]

# Generate answer
def generate_answer(question, context_chunks):
    # Format context text from chunks
    context = "\n\n".join([chunk["text"] for chunk in context_chunks])
    
    # Extract relevant sections from context based on question type
    relevant_sentences = []
    all_sentences = sent_tokenize(context)
    
    # Simplify question for matching
    lower_q = question.lower()
    
    # Look for specific question types and relevant keywords
    if "shareholding" in lower_q or "promoter" in lower_q:
        relevant_sentences = [sent for sent in all_sentences if any(kw in sent.lower() for kw in 
                             ["promoter", "shareholding", "share", "holding", "stake", "%"])]
    
    elif "competitor" in lower_q or "market share" in lower_q:
        relevant_sentences = [sent for sent in all_sentences if any(kw in sent.lower() for kw in 
                             ["competitor", "market share", "amul", "kwality", "mother dairy", "largest"])]
    
    elif "financial" in lower_q or "revenue" in lower_q or "profit" in lower_q:
        relevant_sentences = [sent for sent in all_sentences if any(kw in sent.lower() for kw in 
                             ["crore", "revenue", "profit", "ebitda", "fy", "financial", "₹"])]
    
    elif "trend" in lower_q or "industry" in lower_q:
        relevant_sentences = [sent for sent in all_sentences if any(kw in sent.lower() for kw in 
                             ["trend", "growth", "industry", "market", "consumer", "demand"])]
    
    elif "facilities" in lower_q or "plant" in lower_q or "manufacturing" in lower_q:
        relevant_sentences = [sent for sent in all_sentences if any(kw in sent.lower() for kw in 
                             ["plant", "manufacturing", "facility", "production", "factory", "capacity"])]
    
    else:
        # For general questions, use the first few sentences from each chunk
        for chunk in context_chunks:
            chunk_sentences = sent_tokenize(chunk["text"])
            relevant_sentences.extend(chunk_sentences[:3])
    
    # Deduplicate sentences while maintaining order
    seen = set()
    unique_relevant_sentences = []
    for s in relevant_sentences:
        if s not in seen:
            seen.add(s)
            unique_relevant_sentences.append(s)
    
    # Format the answer
    answer = ""
    
    # Determine the question type for better formatting
    if "shareholding" in lower_q:
        answer += "## Shareholding Breakdown of Vadilal Group\n\n"
        
        # Extract specific shareholding data
        promoter_pattern = r"promoter.*?(\d+\.\d+)%"
        public_pattern = r"public.*?(\d+\.\d+)%"
        fii_pattern = r"(foreign institutional investors|fii).*?(\d+\.\d+)%"
        
        promoter_match = re.search(promoter_pattern, context.lower())
        public_match = re.search(public_pattern, context.lower())
        fii_match = re.search(fii_pattern, context.lower())
        
        if promoter_match:
            answer += f"- **Promoter & Promoter Group**: {promoter_match.group(1)}%\n"
        if public_match:
            answer += f"- **Public**: {public_match.group(1)}%\n"
        if fii_match:
            answer += f"- **Foreign Institutional Investors**: {fii_match.group(2)}%\n"
        
        answer += "\n"
    
    elif "competitor" in lower_q:
        answer += "## Major Competitors of Vadilal Group\n\n"
    
    elif "financial" in lower_q:
        answer += "## Financial Performance Over Last 3 Years\n\n"
        
        # Try to extract financial data for specific years
        years = ["2021-22", "2022-23", "2023-24"]
        found_data = False
        
        for year in years:
            year_pattern = rf"FY\s*{year}.*?revenue.*?(₹|Rs\.?)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*crore"
            profit_pattern = rf"FY\s*{year}.*?profit.*?(₹|Rs\.?)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*crore"
            
            year_match = re.search(year_pattern, context.lower())
            profit_match = re.search(profit_pattern, context.lower())
            
            if year_match or profit_match:
                found_data = True
                answer += f"### FY {year}\n"
                if year_match:
                    answer += f"- **Revenue**: ₹{year_match.group(2)} crore\n"
                if profit_match:
                    answer += f"- **Net Profit**: ₹{profit_match.group(2)} crore\n"
                answer += "\n"
        
        if not found_data:
            answer += " ".join(unique_relevant_sentences[:10])
    
    elif "trend" in lower_q or "industry" in lower_q:
        answer += "## Key Trends in the Indian Ice Cream Industry (2025)\n\n"
    
    else:
        answer += "## Information About Vadilal Group\n\n"
    
    # If we haven't added specific structured content yet, add the relevant sentences
    if len(answer.split("\n")) < 5:
        answer += " ".join(unique_relevant_sentences)
    
    return answer

# Load data on app start
if not st.session_state.chunks:
    with st.spinner("Loading knowledge base..."):
        st.session_state.chunks, st.session_state.tfidf_matrix, st.session_state.vectorizer = load_and_process_data()
    st.success(f"Knowledge base loaded with {len(st.session_state.chunks)} information chunks")

# Sidebar with example questions
st.sidebar.markdown('<h2 class="sub-header">Sample Questions</h2>', unsafe_allow_html=True)

example_questions = [
    "What is the shareholding breakdown of Vadilal Group?",
    "Who are the biggest direct competitors of the company?",
    "What has been the historical financial performance over the last 3 financial years?",
    "What are the key trends driving the Indian ice cream industry in 2025?",
    "How many manufacturing facilities does Vadilal have?",
    "What is Vadilal's international presence?",
    "What is the EBITDA margin trend for Vadilal?",
    "Who are the key leaders in Vadilal Group?"
]

for q in example_questions:
    if st.sidebar.button(q):
        st.session_state.question = q

# Main area
if "question" not in st.session_state:
    st.session_state.question = ""

# User input
question = st.text_input("Your question:", value=st.session_state.question)

if question:
    with st.spinner("Searching for information..."):
        # Search for relevant chunks
        relevant_chunks = search_relevant_chunks(question)
        
        # Generate answer
        answer = generate_answer(question, relevant_chunks)
        
        # Display answer
        st.markdown("### Answer")
        st.markdown(answer)
        
        # Display sources
        with st.expander("Sources"):
            for i, chunk in enumerate(relevant_chunks):
                st.markdown(f"**Source {i+1} ({chunk['section']}):**")
                st.text(chunk["text"][:300] + "...")
