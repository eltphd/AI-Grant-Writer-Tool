"""Embedding utilities for contextual recall and semantic search.

This module provides functions for creating, storing, and retrieving embeddings
for rapid contextual recall in RAG applications.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
import hashlib

# Try to import numpy with graceful fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("⚠️ numpy not available. Some embedding features may be limited.")
    NUMPY_AVAILABLE = False

# Import config
try:
    from . import config
except ImportError:
    import config

# Import privacy utilities
try:
    from . import privacy_utils
except ImportError:
    import privacy_utils

class EmbeddingManager:
    """Manages embeddings for contextual recall and semantic search."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = config.OPENAI_EMBEDDING_MODEL
        self.chunk_size = config.CHUNK_SIZE
        self.privacy_manager = privacy_utils.privacy_manager
    
    def create_embeddings_for_text(self, text: str, project_id: str, content_type: str = "text") -> List[Dict[str, Any]]:
        """Create embeddings for text with privacy protection."""
        # Process text for privacy compliance
        storage_record = self.privacy_manager.process_text_for_storage(text, project_id, content_type)
        
        # Chunk the redacted text
        chunks = self._chunk_text(storage_record["redacted_text"])
        
        # Create embeddings for each chunk
        embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = self._create_embedding(chunk)
            if embedding:
                embedding_record = {
                    "id": f"{storage_record['id']}_chunk_{i}",
                    "project_id": project_id,
                    "content_type": content_type,
                    "content_id": storage_record['id'],
                    "content_text": chunk,
                    "embedding_vector": embedding,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "metadata": {
                        "original_length": len(text),
                        "redacted_length": len(storage_record["redacted_text"]),
                        "entities_detected": len(storage_record["entities"]),
                        "privacy_level": storage_record["privacy_level"]
                    },
                    "created_at": datetime.now().isoformat()
                }
                embeddings.append(embedding_record)
        
        return embeddings
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for embedding."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return None
    
    def semantic_search(self, query: str, project_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search for relevant content."""
        try:
            # Create embedding for query
            query_embedding = self._create_embedding(query)
            if not query_embedding:
                return []
            
            # Get embeddings for project (this would come from database)
            project_embeddings = self._get_project_embeddings(project_id)
            
            # Calculate similarities
            similarities = []
            for emb_record in project_embeddings:
                similarity = self._cosine_similarity(query_embedding, emb_record["embedding_vector"])
                similarities.append({
                    "similarity": similarity,
                    "record": emb_record
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return [item["record"] for item in similarities[:top_k]]
            
        except Exception as e:
            print(f"❌ Error in semantic search: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not NUMPY_AVAILABLE:
            # Fallback to manual calculation without numpy
            if len(vec1) != len(vec2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        
        try:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def _get_project_embeddings(self, project_id: str) -> List[Dict[str, Any]]:
        """Get embeddings for a project (placeholder - would query database)."""
        # This would query the embeddings table
        # For now, return empty list
        return []
    
    def create_context_for_ai(self, query: str, project_id: str, max_context_length: int = 4000) -> str:
        """Create context for AI using semantic search and privacy-safe content."""
        # Perform semantic search
        relevant_records = self.semantic_search(query, project_id, top_k=10)
        
        # Build context from relevant records
        context_parts = []
        current_length = 0
        
        for record in relevant_records:
            content_text = record.get("content_text", "")
            if current_length + len(content_text) > max_context_length:
                break
            
            context_parts.append(content_text)
            current_length += len(content_text)
        
        return "\n\n".join(context_parts)
    
    def update_embeddings_for_project(self, project_id: str, new_text: str, content_type: str = "text") -> bool:
        """Update embeddings when new content is added to a project."""
        try:
            # Create new embeddings
            new_embeddings = self.create_embeddings_for_text(new_text, project_id, content_type)
            
            # Store embeddings (this would save to database)
            # For now, just return success
            return len(new_embeddings) > 0
            
        except Exception as e:
            print(f"❌ Error updating embeddings: {e}")
            return False
    
    def get_embedding_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics about embeddings for a project."""
        # This would query the database
        return {
            "project_id": project_id,
            "total_embeddings": 0,
            "total_chunks": 0,
            "average_chunk_size": 0,
            "last_updated": datetime.now().isoformat()
        }

# Global instance
embedding_manager = EmbeddingManager() 