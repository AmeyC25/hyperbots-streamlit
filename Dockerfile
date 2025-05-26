FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/documents data/chroma_db

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &\n\
streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n\
wait' > start.sh && chmod +x start.sh

CMD ["./start.sh"]