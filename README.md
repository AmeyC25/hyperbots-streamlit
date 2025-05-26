##Document-Based QA Chatbot with ReAct Architecture

This is a document-based chatbot application that uses the ReAct (Reasoning + Acting) paradigm for answering user questions based on uploaded documents. It includes a FastAPI backend for APIs and a Streamlit frontend for user interaction. Documents are embedded into a vector store (ChromaDB), and queries are processed using OpenAI's GPT API.

#Project Structure:

doc-qa-chatbot/

config/

settings.py: Configuration parameters like chunk size, temperature, etc.

data/ (auto-generated)

documents/: Stores uploaded documents

chroma_db/: Stores vector database

src/

api/

main.py: FastAPI routes

chatbot/: Core chatbot logic (ReAct agents, tools, chains)

utils/: Helper functions

tests/: Unit tests

app.py: Streamlit frontend

Dockerfile: Docker image config

docker-compose.yml: Docker service definition

.env: Environment variables (API keys, paths)

requirements.txt: Python dependencies

venv/: Virtual environment (auto-generated)

#Setup Instructions:

Prerequisites:

Python 3.9+

Docker (optional)

OpenAI API Key

#Local Setup:

Clone the repository and navigate to the folder.

Create a virtual environment using: python -m venv venv

#Activate it:

Linux/Mac: source venv/bin/activate

Windows: venv\Scripts\activate

#Install dependencies: pip install -r requirements.txt

Create a .env file with:
OPENAI_API_KEY=your_api_key_here
CHROMA_DB_PATH=./data/chroma_db
UPLOAD_DIR=./data/documents

Make data directories: mkdir -p data/documents data/chroma_db

Running the Application:

Option 1 - Development Mode:

Terminal 1: uvicorn src.api.main:app --reload --port 8000

Terminal 2: streamlit run app.py --server.port 8501

Option 2 - Production Mode (Docker):

docker-compose up --build

To stop: docker-compose down

Accessing the App:

Streamlit UI: http://localhost:8501

FastAPI Docs: http://localhost:8000/docs

#Usage Guide:

Upload documents from the Streamlit sidebar (supports PDF, DOCX, TXT).

Type a question in the input box and submit.

The model returns an answer with supporting context.

#API Endpoints:

POST /upload : Upload a document

POST /query : Ask a question

GET /stats : Get system usage statistics

#Configuration:

Settings can be adjusted in config/settings.py:

chunk_size = 1000

chunk_overlap = 200

max_tokens = 4000

temperature = 0.7

#Testing:

Run tests: pytest src/tests/ -v
Manual API test: curl -X GET http://localhost:8000/stats

#Troubleshooting:

If OpenAI API Key is missing, ensure .env is created properly and restart.

If ports are busy, change them in docker-compose.yml or run commands with different ports.

If document processing fails, check file types or permissions.

If Docker fails to build, try: docker-compose build --no-cache

#Maintenance:

To update dependencies: edit requirements.txt and rebuild using docker-compose up --build
To reset the knowledge base: delete data/chroma_db and restart the app
