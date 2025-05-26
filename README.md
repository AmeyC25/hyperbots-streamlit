Document-Based QA Chatbot with ReAct Architecture
Project Structure
doc-qa-chatbot/
├── config/
│   ├── __pycache__/
│   └── settings.py
├── data/ (auto-generated)
├── src/
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── chatbot/
│   ├── utils/
│   │   └── __init__.py
│   └── tests/
│       ├── __init__.py
│       └── test_basic.py
├── venv/ (auto-generated)
├── .env
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
Setup Instructions
1. Prerequisites
Python 3.9+

Docker (optional)

OpenAI API key

2. Local Setup
bash
# Clone the repository (if applicable)
git clone <your-repo-url>
cd doc-qa-chatbot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "CHROMA_DB_PATH=./data/chroma_db" >> .env
echo "UPLOAD_DIR=./data/documents" >> .env

# Create data directories
mkdir -p data/documents data/chroma_db
3. Running the Application
Option 1: Development Mode
bash
# Terminal 1 - Start FastAPI backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 - Start Streamlit frontend
streamlit run app.py --server.port 8501
Option 2: Production with Docker
bash
# Build and run containers
docker-compose up --build

# To stop
docker-compose down
4. Accessing the Application
Streamlit UI: http://localhost:8501

FastAPI Docs: http://localhost:8000/docs

Usage Guide
1. Uploading Documents
Open the Streamlit UI (http://localhost:8501)

Use the sidebar to upload PDF, DOCX, or TXT files

Click "Upload Document" button

2. Asking Questions
Type your question in the chat input box

Press Enter or click the send button

View the response with reasoning details

3. API Endpoints
POST /upload: Upload documents

POST /query: Submit questions

GET /stats: Get system statistics

Configuration Options
Edit config/settings.py to modify:

python
chunk_size = 1000  # Text chunk size for processing
chunk_overlap = 200  # Overlap between chunks
max_tokens = 4000  # Context window size
temperature = 0.7  # LLM creativity level
Testing
bash
# Run basic tests
pytest tests/ -v

# Test API endpoints manually
curl -X GET http://localhost:8000/stats
Troubleshooting
Common Issues
Missing API Key:

Ensure .env exists with OPENAI_API_KEY

Restart application after adding key

Port Conflicts:

Change ports in docker-compose.yml or run commands

Document Processing Failures:

Check file permissions

Verify supported formats (PDF, DOCX, TXT)

Docker Build Issues:

Clean build: docker-compose build --no-cache

Maintenance
Updating Dependencies
Update requirements.txt

Rebuild containers:

bash
docker-compose up --build
Resetting the Knowledge Base
Delete contents of data/chroma_db

Restart the application


