# Document-Based QA Chatbot with ReAct Architecture

This is a document-based chatbot application that uses the ReAct (Reasoning + Acting) paradigm for answering user questions based on uploaded documents. It includes a FastAPI backend for APIs and a Streamlit frontend for user interaction. Documents are embedded into a vector store (ChromaDB), and queries are processed using OpenAI's GPT API.

## 📁 Project Structure

doc-qa-chatbot/  
├── config/  
│   └── settings.py  
├── data/ (auto-generated)  
│   ├── documents/  
│   └── chroma_db/  
├── src/  
│   ├── api/  
│   │   └── main.py  
│   ├── chatbot/  
│   ├── utils/  
│   └── tests/  
├── app.py  
├── .env  
├── .gitignore  
├── Dockerfile  
├── docker-compose.yml  
├── requirements.txt  
└── venv/ (auto-generated)

## ⚙️ Setup Instructions

### 1. Prerequisites
* Python 3.9+
* Docker (optional)
* OpenAI API Key

### 2. Local Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd doc-qa-chatbot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "CHROMA_DB_PATH=./data/chroma_db" >> .env
echo "UPLOAD_DIR=./data/documents" >> .env

# Create required directories
mkdir -p data/documents data/chroma_db

```
🧠 Usage Guide
1. Uploading Documents
Open the Streamlit UI

Upload PDF, DOCX, or TXT files from the sidebar

Click "Upload Document"

2. Asking Questions
Type your question in the input box

Press Enter or click the send button

Get answers with reasoning and context

3. API Endpoints
POST /upload - Upload documents

POST /query - Submit a question

GET /stats - View system stats

