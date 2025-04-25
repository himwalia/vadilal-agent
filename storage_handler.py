import os
import json
import base64
import sqlite3
import streamlit as st
from io import BytesIO
import requests

class StorageHandler:
    """
    Handles persistent storage for Streamlit Cloud deployment.
    Uses SQLite database for storing uploaded text data and embeddings.
    """
    
    def __init__(self):
        # Create database if it doesn't exist
        self.conn = sqlite3.connect('vadilal_data.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        # Table for storing text data
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS text_data (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table for storing vector embeddings
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY,
            chunk_id TEXT NOT NULL,
            chunk_content TEXT NOT NULL,
            embedding BLOB NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    def save_text_data(self, content):
        """Save text data to database."""
        # Clear previous data
        self.cursor.execute("DELETE FROM text_data")
        
        # Insert new data
        self.cursor.execute("INSERT INTO text_data (content) VALUES (?)", (content,))
        self.conn.commit()
        return True
    
    def get_text_data(self):
        """Retrieve text data from database."""
        self.cursor.execute("SELECT content FROM text_data ORDER BY timestamp DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def save_embeddings(self, chunk_id, chunk_content, embedding):
        """Save embedding to database."""
        # Convert embedding to binary
        embedding_binary = base64.b64encode(json.dumps(embedding).encode())
        
        # Check if chunk exists
        self.cursor.execute("SELECT id FROM embeddings WHERE chunk_id = ?", (chunk_id,))
        result = self.cursor.fetchone()
        
        if result:
            # Update existing embedding
            self.cursor.execute(
                "UPDATE embeddings SET chunk_content = ?, embedding = ? WHERE chunk_id = ?", 
                (chunk_content, embedding_binary, chunk_id)
            )
        else:
            # Insert new embedding
            self.cursor.execute(
                "INSERT INTO embeddings (chunk_id, chunk_content, embedding) VALUES (?, ?, ?)",
                (chunk_id, chunk_content, embedding_binary)
            )
        
        self.conn.commit()
        return True
    
    def get_embeddings(self):
        """Retrieve all embeddings from database."""
        self.cursor.execute("SELECT chunk_id, chunk_content, embedding FROM embeddings")
        results = self.cursor.fetchall()
        
        embeddings = {}
        for chunk_id, chunk_content, embedding_binary in results:
            embedding = json.loads(base64.b64decode(embedding_binary))
            embeddings[chunk_id] = {
                "content": chunk_content,
                "embedding": embedding
            }
        
        return embeddings
    
    def close(self):
        """Close database connection."""
        self.conn.close()

# Alternative: GitHub Gist-based storage (if you prefer this over SQLite)
class GistStorageHandler:
    """
    Handles persistent storage using GitHub Gists.
    Requires a GitHub access token with gist permissions.
    """
    
    def __init__(self):
        self.github_token = self._get_github_token()
        self.gist_id = self._get_or_create_gist_id()
    
    def _get_github_token(self):
        # Try to get GitHub token from Streamlit secrets
        try:
            return st.secrets["github"]["token"]
        except (KeyError, FileNotFoundError):
            # Fall back to environment variable (for local development)
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                st.error("GitHub token not found. Please add it to your Streamlit secrets or .env file.")
            return token
    
    def _get_or_create_gist_id(self):
        # Try to get Gist ID from Streamlit secrets
        try:
            return st.secrets["github"]["gist_id"]
        except (KeyError, FileNotFoundError):
            # Fall back to environment variable
            gist_id = os.getenv("GIST_ID")
            
            # Create a new Gist if doesn't exist
            if not gist_id:
                headers = {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                data = {
                    "description": "Vadilal AI Assistant Data",
                    "public": False,
                    "files": {
                        "vadilal_data.txt": {
                            "content": "Initial Vadilal data file."
                        }
                    }
                }
                
                response = requests.post(
                    "https://api.github.com/gists",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 201:
                    gist_id = response.json()["id"]
                    st.warning(f"Created new Gist with ID: {gist_id}. Please add this to your Streamlit secrets.")
                    return gist_id
                else:
                    st.error(f"Failed to create Gist: {response.text}")
                    return None
            
            return gist_id
    
    def save_text_data(self, content):
        """Save text data to GitHub Gist."""
        if not self.github_token or not self.gist_id:
            return False
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "files": {
                "vadilal_data.txt": {
                    "content": content
                }
            }
        }
        
        response = requests.patch(
            f"https://api.github.com/gists/{self.gist_id}",
            headers=headers,
            json=data
        )
        
        return response.status_code == 200
    
    def get_text_data(self):
        """Retrieve text data from GitHub Gist."""
        if not self.github_token or not self.gist_id:
            return None
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            f"https://api.github.com/gists/{self.gist_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            gist_data = response.json()
            if "vadilal_data.txt" in gist_data["files"]:
                return gist_data["files"]["vadilal_data.txt"]["content"]
        
        return None
