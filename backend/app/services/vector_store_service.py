import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging

from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for managing vector storage and retrieval using ChromaDB.
    """
    
    def __init__(self):
        """
        Initialize the ChromaDB client and create the collection.
        """
        # Ensure the ChromaDB directory exists
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create or get the collection for code embeddings
        self.collection = self.client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized with collection 'code_embeddings'")
    
    def add_embeddings(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]],
        documents: List[str]
    ) -> None:
        """
        Add embeddings to the vector store.
        
        Args:
            ids: List of unique IDs for the embeddings
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            documents: List of document texts
        """
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"Added {len(ids)} embeddings to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding embeddings to ChromaDB: {str(e)}")
            raise
    
    def query(
        self, 
        query_embedding: List[float], 
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar embeddings.
        
        Args:
            query_embedding: The query embedding vector
            n_results: Number of results to return
            where: Filter condition for metadata
            
        Returns:
            Dictionary containing query results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise
    
    def get_by_id(self, id: str) -> Dict[str, Any]:
        """
        Get an embedding by its ID.
        
        Args:
            id: The unique ID of the embedding
            
        Returns:
            Dictionary containing the embedding data
        """
        try:
            return self.collection.get(ids=[id])
        except Exception as e:
            logger.error(f"Error getting embedding from ChromaDB: {str(e)}")
            raise
    
    def delete_by_id(self, id: str) -> None:
        """
        Delete an embedding by its ID.
        
        Args:
            id: The unique ID of the embedding to delete
        """
        try:
            self.collection.delete(ids=[id])
            logger.info(f"Deleted embedding with ID {id} from ChromaDB")
        except Exception as e:
            logger.error(f"Error deleting embedding from ChromaDB: {str(e)}")
            raise
    
    def delete_by_repository(self, repo_id: str) -> None:
        """
        Delete all embeddings for a specific repository.
        
        Args:
            repo_id: The repository ID
        """
        try:
            self.collection.delete(where={"repository_id": repo_id})
            logger.info(f"Deleted all embeddings for repository {repo_id} from ChromaDB")
        except Exception as e:
            logger.error(f"Error deleting repository embeddings from ChromaDB: {str(e)}")
            raise

# Create a singleton instance
vector_store = VectorStoreService()