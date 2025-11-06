"""Vector database service for semantic search."""
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
import os
from config import settings
from utils.logger import logger


class VectorDB:
    """FAISS-based vector database for document embeddings."""
    
    def __init__(self, dimension: int = 384, db_path: Optional[str] = None):
        self.dimension = dimension
        self.db_path = db_path or settings.VECTOR_DB_PATH
        self.index = None
        self.metadata = []  # Store metadata for each vector
        self.load_index()
    
    def create_index(self):
        """Create a new FAISS index."""
        # Use L2 distance (Euclidean)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def load_index(self):
        """Load existing index from disk."""
        index_path = os.path.join(self.db_path, "index.faiss")
        metadata_path = os.path.join(self.db_path, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self.create_index()
        else:
            self.create_index()
    
    def save_index(self):
        """Save index to disk."""
        os.makedirs(self.db_path, exist_ok=True)
        index_path = os.path.join(self.db_path, "index.faiss")
        metadata_path = os.path.join(self.db_path, "metadata.pkl")
        
        if self.index is not None:
            faiss.write_index(self.index, index_path)
            with open(metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Saved index with {self.index.ntotal} vectors")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add vectors to the index."""
        if self.index is None:
            self.create_index()
        
        # Ensure vectors are float32
        vectors = vectors.astype("float32")
        
        # Add to index
        self.index.add(vectors)
        
        # Store metadata
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(vectors)} vectors to index")
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Ensure query vector is float32
        query_vector = query_vector.astype("float32").reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                results.append({
                    "index": int(idx),
                    "distance": float(distance),
                    "metadata": self.metadata[int(idx)]
                })
        
        return results
    
    def delete_vector(self, index: int):
        """Delete a vector from the index (not directly supported by FAISS, requires rebuild)."""
        # FAISS doesn't support direct deletion, so we need to rebuild
        # This is a simplified version - in production, use a more efficient approach
        logger.warning("Vector deletion requires index rebuild - not implemented")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata)
        }

