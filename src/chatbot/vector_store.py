import logging
from typing import List, Dict, Any, Optional
import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.persist_directory = settings.chroma_db_path
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store."""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        if not documents:
            logger.warning("No documents to add")
            return []
        
        try:
            # Filter out documents with empty content
            valid_documents = [doc for doc in documents if doc.page_content.strip()]
            
            if not valid_documents:
                logger.warning("No valid documents to add")
                return []
            
            ids = self.vectorstore.add_documents(valid_documents)
            self.vectorstore.persist()
            logger.info(f"Added {len(valid_documents)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return []
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        try:
            if not self.vectorstore:
                logger.error("Vector store not initialized")
                return []
            
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Search for similar documents with similarity scores."""
        try:
            if not self.vectorstore:
                logger.error("Vector store not initialized")
                return []
            
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search with score: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            if not self.vectorstore:
                return {"error": "Vector store not initialized"}
            
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "document_count": count,
                "collection_name": collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}