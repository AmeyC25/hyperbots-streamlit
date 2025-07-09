import streamlit as st
import requests
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Document QA Chatbot",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("📚 DocMate")
    st.markdown("Upload relevant documents and ask questions!")
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt'],
            help="Upload PDF, DOCX, or TXT files"
        )
        
        if uploaded_file is not None:
            if st.button("Upload Document"):
                with st.spinner("Uploading and processing document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_BASE_URL}/upload", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.info(f"Added {result['chunks_added']} text chunks")
                        else:
                            st.error(f"❌ Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Stats section
        st.header("📊 Statistics")
        if st.button("Refresh Stats"):
            try:
                response = requests.get(f"{API_BASE_URL}/stats")
                if response.status_code == 200:
                    stats = response.json()
                    st.json(stats)
                else:
                    st.error("Failed to get stats")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                with st.expander("🔍 Query Details"):
                    st.json(message["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):
                try:
                    # Make API request
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"question": prompt}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result["answer"]
                        metadata = result.get("metadata", {})
                        
                        # Display answer
                        st.markdown(answer)
                        
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "metadata": metadata
                        })
                        
                        # Show metadata
                        if metadata:
                            with st.expander("🔍 Query Details"):
                                st.json(metadata)
                    
                    else:
                        error_msg = f"❌ Error: {response.status_code} - {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                
                except Exception as e:
                    error_msg = f"❌ Connection error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()
