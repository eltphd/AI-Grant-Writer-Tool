import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Use the Supabase client for all database interactions
try:
    from . import supabase_utils as db_manager
except ImportError:
    import supabase_utils as db_manager

class SupabaseRAG:
    """RAG implementation using Supabase for data storage and retrieval."""

    def get_relevant_context(self, question: str, files: List[str]) -> str:
        """Get the most relevant context from Supabase using vector similarity search.
        
        Args:
            question: The user's question.
            files: A list of file names to search within.
            
        Returns:
            The most relevant text chunk.
        """
        # Call the Supabase Edge Function to get the best matching context
        return db_manager.rag_context(question, files)

# Global instance of the SupabaseRAG class
rag_db = SupabaseRAG() 