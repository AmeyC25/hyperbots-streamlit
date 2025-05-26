import logging
from typing import Dict, Any, List
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .executor import QueryExecutor
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentQAChatbot:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.executor = QueryExecutor(self.vector_store)
        self._initialized = False
    
    def initialize(self):
        """Initialize the chatbot by loading existing documents."""
        try:
            # Load documents from the upload directory
            documents = self.document_processor.process_directory(settings.upload_dir)
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Initialized with {len(documents)} document chunks")
            else:
                logger.info("No documents found in upload directory")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")
            raise
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a new document to the knowledge base."""
        try:
            documents = self.document_processor.process_document(file_path)
            if documents:
                ids = self.vector_store.add_documents(documents)
                return {
                    "success": True,
                    "message": f"Added {len(documents)} chunks from {file_path}",
                    "chunk_count": len(documents),
                    "document_ids": ids
                }
            else:
                return {
                    "success": False,
                    "message": f"No content extracted from {file_path}"
                }
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            return {
                "success": False,
                "message": f"Error adding document: {str(e)}"
            }
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a query and return answer."""
        if not self._initialized:
            self.initialize()
        
        try:
            result = self.executor.execute_query(question)
            return result
        except Exception as e:
            logger.error(f"Error processing query '{question}': {e}")
            return {
                "query": question,
                "answer": f"Error processing query: {str(e)}",
                "error": True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics."""
        try:
            collection_info = self.vector_store.get_collection_info()
            return {
                "initialized": self._initialized,
                "document_chunks": collection_info.get("document_count", 0),
                "vector_store_info": collection_info
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

# Create global instance
chatbot = DocumentQAChatbot()