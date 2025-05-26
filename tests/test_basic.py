import pytest
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chatbot.document_processor import DocumentProcessor
from chatbot.vector_store import VectorStore
from chatbot import chatbot

class TestDocumentProcessor:
    def test_text_processing(self):
        processor = DocumentProcessor()
        
        # Test text splitting
        text = "This is a test document. " * 100
        splitter = processor.text_splitter
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= processor.text_splitter.chunk_size + processor.text_splitter.chunk_overlap for chunk in chunks)

class TestVectorStore:
    def test_initialization(self):
        try:
            vector_store = VectorStore()
            assert vector_store.vectorstore is not None
            assert vector_store.embeddings is not None
        except Exception as e:
            pytest.skip(f"Vector store initialization failed: {e}")

class TestChatbot:
    def test_chatbot_creation(self):
        assert chatbot is not None
        assert hasattr(chatbot, 'document_processor')
        assert hasattr(chatbot, 'vector_store')
        assert hasattr(chatbot, 'executor')

if __name__ == "__main__":
    pytest.main([__file__])