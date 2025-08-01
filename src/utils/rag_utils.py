import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class KnowledgeItem:
    """Represents a knowledge item in the database"""
    id: str
    title: str
    content: str
    category: str  # 'grant_narrative', 'community_profile', 'cultural_guide', 'best_practice'
    tags: List[str]
    source: str
    created_at: str
    cultural_context: Optional[str] = None
    community_focus: Optional[str] = None
    success_metrics: Optional[Dict] = None

@dataclass
class CulturalGuideline:
    """Represents cultural competency guidelines"""
    id: str
    community: str
    guidelines: List[str]
    cultural_sensitivities: List[str]
    language_preferences: List[str]
    best_practices: List[str]
    created_at: str

@dataclass
class CommunityProfile:
    """Represents community demographic and cultural information"""
    id: str
    community_name: str
    demographics: Dict[str, Any]
    cultural_backgrounds: List[str]
    languages: List[str]
    key_concerns: List[str]
    strengths: List[str]
    created_at: str

class RAGDatabase:
    """RAG Database for storing and retrieving knowledge items"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.knowledge_dir = os.path.join(data_dir, "knowledge")
        self.cultural_dir = os.path.join(data_dir, "cultural")
        self.community_dir = os.path.join(data_dir, "communities")
        
        # Ensure directories exist
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.cultural_dir, exist_ok=True)
        os.makedirs(self.community_dir, exist_ok=True)
        
        # Initialize vectorizer for semantic search
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Load and index existing data
        self._load_and_index_data()
    
    def _load_and_index_data(self):
        """Load existing data and create search index"""
        self.knowledge_items = []
        self.cultural_guidelines = []
        self.community_profiles = []
        
        # Load knowledge items
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.knowledge_dir, filename), 'r') as f:
                    data = json.load(f)
                    self.knowledge_items.append(KnowledgeItem(**data))
        
        # Load cultural guidelines
        for filename in os.listdir(self.cultural_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.cultural_dir, filename), 'r') as f:
                    data = json.load(f)
                    self.cultural_guidelines.append(CulturalGuideline(**data))
        
        # Load community profiles
        for filename in os.listdir(self.community_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.community_dir, filename), 'r') as f:
                    data = json.load(f)
                    self.community_profiles.append(CommunityProfile(**data))
        
        # Create search index
        self._create_search_index()
    
    def _create_search_index(self):
        """Create TF-IDF search index from knowledge items"""
        if not self.knowledge_items:
            return
        
        # Combine all text for vectorization
        all_texts = []
        for item in self.knowledge_items:
            text = f"{item.title} {item.content} {' '.join(item.tags)}"
            if item.cultural_context:
                text += f" {item.cultural_context}"
            if item.community_focus:
                text += f" {item.community_focus}"
            all_texts.append(text)
        
        # Fit vectorizer and create matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(all_texts)
    
    def add_knowledge_item(self, item: KnowledgeItem) -> bool:
        """Add a new knowledge item to the database"""
        try:
            # Save to file
            filename = f"{item.id}.json"
            filepath = os.path.join(self.knowledge_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(item), f, indent=2)
            
            # Add to memory and update index
            self.knowledge_items.append(item)
            self._create_search_index()
            
            return True
        except Exception as e:
            print(f"Error adding knowledge item: {e}")
            return False
    
    def add_cultural_guideline(self, guideline: CulturalGuideline) -> bool:
        """Add cultural competency guidelines"""
        try:
            filename = f"{guideline.id}.json"
            filepath = os.path.join(self.cultural_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(guideline), f, indent=2)
            
            self.cultural_guidelines.append(guideline)
            return True
        except Exception as e:
            print(f"Error adding cultural guideline: {e}")
            return False
    
    def add_community_profile(self, profile: CommunityProfile) -> bool:
        """Add community profile"""
        try:
            filename = f"{profile.id}.json"
            filepath = os.path.join(self.community_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            
            self.community_profiles.append(profile)
            return True
        except Exception as e:
            print(f"Error adding community profile: {e}")
            return False
    
    def search_knowledge(self, query: str, category: Optional[str] = None, 
                        limit: int = 5) -> List[KnowledgeItem]:
        """Search knowledge items using TF-IDF similarity"""
        if not self.knowledge_items or not hasattr(self, 'tfidf_matrix'):
            return []
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            item = self.knowledge_items[idx]
            if category is None or item.category == category:
                results.append(item)
        
        return results
    
    def get_cultural_guidelines(self, community: Optional[str] = None) -> List[CulturalGuideline]:
        """Get cultural guidelines for specific community or all"""
        if community:
            return [g for g in self.cultural_guidelines if g.community.lower() == community.lower()]
        return self.cultural_guidelines
    
    def get_community_profile(self, community_name: str) -> Optional[CommunityProfile]:
        """Get community profile by name"""
        for profile in self.community_profiles:
            if profile.community_name.lower() == community_name.lower():
                return profile
        return None
    
    def get_relevant_context(self, query: str, section_type: str, 
                           community_context: Optional[str] = None) -> Dict[str, Any]:
        """Get relevant context for grant section generation"""
        context = {
            'knowledge_items': [],
            'cultural_guidelines': [],
            'community_profile': None,
            'best_practices': []
        }
        
        # Search for relevant knowledge items
        search_query = f"{section_type} {query}"
        knowledge_items = self.search_knowledge(search_query, limit=3)
        context['knowledge_items'] = knowledge_items
        
        # Get cultural guidelines if community context provided
        if community_context:
            cultural_guidelines = self.get_cultural_guidelines(community_context)
            context['cultural_guidelines'] = cultural_guidelines
            
            # Get community profile
            community_profile = self.get_community_profile(community_context)
            context['community_profile'] = community_profile
        
        # Get best practices for the section type
        best_practices = self.search_knowledge(f"best practice {section_type}", 
                                             category="best_practice", limit=2)
        context['best_practices'] = best_practices
        
        return context

# Global RAG database instance
rag_db = RAGDatabase() 