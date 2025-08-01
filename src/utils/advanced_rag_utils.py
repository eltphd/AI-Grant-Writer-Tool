"""Advanced RAG system using ChromaDB and sentence transformers for cultural competency.

This module implements a sophisticated RAG system that can handle:
- Multilingual content and cultural contexts
- Advanced semantic search with embeddings
- Cultural competency guidelines integration
- Community-specific knowledge bases
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

# Advanced RAG Dependencies
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer, AutoModel
    import torch
    ADVANCED_RAG_AVAILABLE = True
except ImportError:
    ADVANCED_RAG_AVAILABLE = False
    print("⚠️ Advanced RAG dependencies not available. Using fallback.")

@dataclass
class CulturalKnowledgeItem:
    """Advanced knowledge item with cultural context"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    source: str
    created_at: str
    cultural_context: Optional[str] = None
    community_focus: Optional[str] = None
    language: str = "en"
    cultural_sensitivity_score: Optional[float] = None
    community_relevance_score: Optional[float] = None
    embedding: Optional[List[float]] = None

@dataclass
class CulturalGuideline:
    """Enhanced cultural competency guidelines"""
    id: str
    community: str
    guidelines: List[str]
    cultural_sensitivities: List[str]
    language_preferences: List[str]
    best_practices: List[str]
    cultural_norms: Dict[str, Any]
    communication_style: str
    created_at: str

@dataclass
class CommunityProfile:
    """Enhanced community demographic and cultural information"""
    id: str
    community_name: str
    demographics: Dict[str, Any]
    cultural_backgrounds: List[str]
    languages: List[str]
    key_concerns: List[str]
    strengths: List[str]
    cultural_values: Dict[str, Any]
    communication_preferences: Dict[str, Any]
    created_at: str

class AdvancedRAGSystem:
    """Advanced RAG system using ChromaDB and sentence transformers"""
    
    def __init__(self, data_dir: str = "data", use_advanced: bool = True):
        self.data_dir = data_dir
        self.use_advanced = use_advanced and ADVANCED_RAG_AVAILABLE
        
        # Initialize directories
        self._setup_directories()
        
        if self.use_advanced:
            self._initialize_advanced_rag()
        else:
            self._initialize_fallback_rag()
    
    def _setup_directories(self):
        """Setup data directories"""
        directories = [
            "knowledge",
            "cultural", 
            "communities",
            "embeddings",
            "cultural_datasets"
        ]
        
        for dir_name in directories:
            os.makedirs(os.path.join(self.data_dir, dir_name), exist_ok=True)
    
    def _initialize_advanced_rag(self):
        """Initialize advanced RAG with ChromaDB and sentence transformers"""
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=os.path.join(self.data_dir, "chroma_db"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collections
            self.knowledge_collection = self.chroma_client.get_or_create_collection(
                name="cultural_knowledge",
                metadata={"description": "Cultural knowledge base for grant writing"}
            )
            
            self.cultural_collection = self.chroma_client.get_or_create_collection(
                name="cultural_guidelines",
                metadata={"description": "Cultural competency guidelines"}
            )
            
            self.community_collection = self.chroma_client.get_or_create_collection(
                name="community_profiles",
                metadata={"description": "Community demographic and cultural profiles"}
            )
            
            # Initialize sentence transformer for multilingual support
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load cultural competency datasets
            self._load_cultural_datasets()
            
            print("✅ Advanced RAG system initialized with ChromaDB and sentence transformers")
            
        except Exception as e:
            print(f"❌ Error initializing advanced RAG: {e}")
            self.use_advanced = False
            self._initialize_fallback_rag()
    
    def _initialize_fallback_rag(self):
        """Initialize fallback RAG system"""
        print("⚠️ Using fallback RAG system")
        self.knowledge_items = []
        self.cultural_guidelines = []
        self.community_profiles = []
        self._load_existing_data()
    
    def _load_cultural_datasets(self):
        """Load cultural competency datasets"""
        cultural_datasets_dir = os.path.join(self.data_dir, "cultural_datasets")
        
        # Create sample cultural datasets if they don't exist
        self._create_sample_cultural_datasets(cultural_datasets_dir)
        
        # Load datasets
        self.cultural_datasets = {}
        for filename in os.listdir(cultural_datasets_dir):
            if filename.endswith('.json'):
                with open(os.path.join(cultural_datasets_dir, filename), 'r') as f:
                    data = json.load(f)
                    self.cultural_datasets[filename.replace('.json', '')] = data
    
    def _create_sample_cultural_datasets(self, datasets_dir: str):
        """Create sample cultural competency datasets"""
        
        # Grant writing cultural guidelines
        grant_cultural_guidelines = {
            "grant_writing_cultural_guidelines": {
                "description": "Cultural guidelines for grant writing",
                "guidelines": [
                    "Use inclusive language that respects diverse communities",
                    "Highlight community strengths and resilience",
                    "Avoid deficit-based language and stereotypes",
                    "Emphasize community-driven solutions",
                    "Include cultural context in project descriptions",
                    "Use culturally appropriate examples and analogies",
                    "Consider community communication preferences",
                    "Address cultural barriers to access and participation"
                ],
                "cultural_sensitivities": [
                    "Avoid assuming cultural homogeneity",
                    "Respect traditional knowledge and practices",
                    "Acknowledge historical context and systemic barriers",
                    "Use community-preferred terminology",
                    "Consider cultural concepts of time and planning"
                ],
                "best_practices": [
                    "Engage community members in proposal development",
                    "Include cultural competency in evaluation metrics",
                    "Provide culturally appropriate outreach strategies",
                    "Consider language access and translation needs",
                    "Address cultural barriers to participation"
                ]
            }
        }
        
        # Community profiles
        community_profiles = {
            "urban_communities": {
                "demographics": {"diversity": "high", "languages": ["en", "es", "zh"]},
                "cultural_values": {"community": "strong", "resilience": "high"},
                "communication_preferences": {"direct": True, "formal": False}
            },
            "rural_communities": {
                "demographics": {"diversity": "moderate", "languages": ["en"]},
                "cultural_values": {"tradition": "strong", "self_reliance": "high"},
                "communication_preferences": {"personal": True, "trust_based": True}
            },
            "indigenous_communities": {
                "demographics": {"diversity": "high", "languages": ["en", "native"]},
                "cultural_values": {"spirituality": "strong", "land_connection": "high"},
                "communication_preferences": {"respectful": True, "traditional": True}
            }
        }
        
        # Save datasets
        for name, data in grant_cultural_guidelines.items():
            filepath = os.path.join(datasets_dir, f"{name}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
        
        for name, data in community_profiles.items():
            filepath = os.path.join(datasets_dir, f"{name}_profile.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
    
    def add_knowledge_item(self, item: CulturalKnowledgeItem) -> bool:
        """Add knowledge item with cultural context"""
        try:
            if self.use_advanced:
                return self._add_knowledge_item_advanced(item)
            else:
                return self._add_knowledge_item_fallback(item)
        except Exception as e:
            print(f"Error adding knowledge item: {e}")
            return False
    
    def _add_knowledge_item_advanced(self, item: CulturalKnowledgeItem) -> bool:
        """Add knowledge item using advanced RAG"""
        try:
            # Generate embedding
            text_for_embedding = f"{item.title} {item.content} {' '.join(item.tags)}"
            if item.cultural_context:
                text_for_embedding += f" {item.cultural_context}"
            
            embedding = self.embedding_model.encode(text_for_embedding).tolist()
            item.embedding = embedding
            
            # Add to ChromaDB
            self.knowledge_collection.add(
                documents=[item.content],
                metadatas=[{
                    "title": item.title,
                    "category": item.category,
                    "tags": ",".join(item.tags),
                    "cultural_context": item.cultural_context or "",
                    "community_focus": item.community_focus or "",
                    "language": item.language,
                    "source": item.source,
                    "created_at": item.created_at
                }],
                embeddings=[embedding],
                ids=[item.id]
            )
            
            # Save to file for persistence
            self._save_knowledge_item_file(item)
            
            return True
            
        except Exception as e:
            print(f"Error in advanced knowledge item addition: {e}")
            return False
    
    def _add_knowledge_item_fallback(self, item: CulturalKnowledgeItem) -> bool:
        """Add knowledge item using fallback method"""
        try:
            self.knowledge_items.append(item)
            self._save_knowledge_item_file(item)
            return True
        except Exception as e:
            print(f"Error in fallback knowledge item addition: {e}")
            return False
    
    def _save_knowledge_item_file(self, item: CulturalKnowledgeItem):
        """Save knowledge item to file"""
        filename = f"{item.id}.json"
        filepath = os.path.join(self.data_dir, "knowledge", filename)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(item), f, indent=2)
    
    def search_knowledge(self, query: str, category: Optional[str] = None, 
                        community_context: Optional[str] = None, limit: int = 5) -> List[CulturalKnowledgeItem]:
        """Search knowledge with cultural context awareness"""
        try:
            if self.use_advanced:
                return self._search_knowledge_advanced(query, category, community_context, limit)
            else:
                return self._search_knowledge_fallback(query, category, community_context, limit)
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    def _search_knowledge_advanced(self, query: str, category: Optional[str] = None,
                                 community_context: Optional[str] = None, limit: int = 5) -> List[CulturalKnowledgeItem]:
        """Advanced semantic search with cultural context"""
        try:
            # Enhance query with cultural context
            enhanced_query = query
            if community_context:
                enhanced_query += f" {community_context}"
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(enhanced_query).tolist()
            
            # Search in ChromaDB
            where_clause = {}
            if category:
                where_clause["category"] = category
            
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Convert results to CulturalKnowledgeItem objects
            items = []
            for i in range(len(results['ids'][0])):
                item = CulturalKnowledgeItem(
                    id=results['ids'][0][i],
                    title=results['metadatas'][0][i]['title'],
                    content=results['documents'][0][i],
                    category=results['metadatas'][0][i]['category'],
                    tags=results['metadatas'][0][i]['tags'].split(',') if results['metadatas'][0][i]['tags'] else [],
                    source=results['metadatas'][0][i]['source'],
                    created_at=results['metadatas'][0][i]['created_at'],
                    cultural_context=results['metadatas'][0][i]['cultural_context'],
                    community_focus=results['metadatas'][0][i]['community_focus'],
                    language=results['metadatas'][0][i]['language']
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"Error in advanced search: {e}")
            return []
    
    def _search_knowledge_fallback(self, query: str, category: Optional[str] = None,
                                 community_context: Optional[str] = None, limit: int = 5) -> List[CulturalKnowledgeItem]:
        """Fallback search using simple text matching"""
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_items:
            if category and item.category != category:
                continue
            
            # Simple text matching
            if (query_lower in item.title.lower() or 
                query_lower in item.content.lower() or
                any(tag.lower() in query_lower for tag in item.tags)):
                results.append(item)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_cultural_guidelines(self, community: Optional[str] = None) -> List[CulturalGuideline]:
        """Get cultural guidelines for specific community"""
        try:
            if self.use_advanced:
                return self._get_cultural_guidelines_advanced(community)
            else:
                return self._get_cultural_guidelines_fallback(community)
        except Exception as e:
            print(f"Error getting cultural guidelines: {e}")
            return []
    
    def _get_cultural_guidelines_advanced(self, community: Optional[str] = None) -> List[CulturalGuideline]:
        """Get cultural guidelines using advanced search"""
        try:
            where_clause = {}
            if community:
                where_clause["community"] = community
            
            results = self.cultural_collection.query(
                query_texts=["cultural guidelines"],
                n_results=10,
                where=where_clause if where_clause else None
            )
            
            guidelines = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                guideline = CulturalGuideline(
                    id=results['ids'][0][i],
                    community=metadata['community'],
                    guidelines=metadata['guidelines'].split('|') if metadata['guidelines'] else [],
                    cultural_sensitivities=metadata['cultural_sensitivities'].split('|') if metadata['cultural_sensitivities'] else [],
                    language_preferences=metadata['language_preferences'].split('|') if metadata['language_preferences'] else [],
                    best_practices=metadata['best_practices'].split('|') if metadata['best_practices'] else [],
                    cultural_norms=json.loads(metadata['cultural_norms']) if metadata['cultural_norms'] else {},
                    communication_style=metadata['communication_style'],
                    created_at=metadata['created_at']
                )
                guidelines.append(guideline)
            
            return guidelines
            
        except Exception as e:
            print(f"Error in advanced cultural guidelines: {e}")
            return []
    
    def _get_cultural_guidelines_fallback(self, community: Optional[str] = None) -> List[CulturalGuideline]:
        """Get cultural guidelines using fallback method"""
        results = []
        for guideline in self.cultural_guidelines:
            if not community or guideline.community == community:
                results.append(guideline)
        return results
    
    def get_relevant_context(self, query: str, section_type: str, 
                           community_context: Optional[str] = None) -> Dict[str, Any]:
        """Get culturally relevant context for grant writing"""
        try:
            # Search for relevant knowledge
            knowledge_items = self.search_knowledge(query, limit=5)
            
            # Get cultural guidelines
            cultural_guidelines = self.get_cultural_guidelines(community_context)
            
            # Get community profiles
            community_profiles = self._get_community_profiles(community_context)
            
            # Build context
            context = {
                "knowledge_items": [asdict(item) for item in knowledge_items],
                "cultural_guidelines": [asdict(guideline) for guideline in cultural_guidelines],
                "community_profiles": [asdict(profile) for profile in community_profiles],
                "section_type": section_type,
                "community_context": community_context,
                "cultural_context": self._extract_cultural_context(knowledge_items, cultural_guidelines)
            }
            
            return context
            
        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return {}
    
    def _get_community_profiles(self, community_context: Optional[str] = None) -> List[CommunityProfile]:
        """Get community profiles"""
        try:
            if self.use_advanced:
                return self._get_community_profiles_advanced(community_context)
            else:
                return self._get_community_profiles_fallback(community_context)
        except Exception as e:
            print(f"Error getting community profiles: {e}")
            return []
    
    def _get_community_profiles_advanced(self, community_context: Optional[str] = None) -> List[CommunityProfile]:
        """Get community profiles using advanced search"""
        try:
            where_clause = {}
            if community_context:
                where_clause["community_name"] = community_context
            
            results = self.community_collection.query(
                query_texts=["community profile"],
                n_results=5,
                where=where_clause if where_clause else None
            )
            
            profiles = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                profile = CommunityProfile(
                    id=results['ids'][0][i],
                    community_name=metadata['community_name'],
                    demographics=json.loads(metadata['demographics']) if metadata['demographics'] else {},
                    cultural_backgrounds=metadata['cultural_backgrounds'].split('|') if metadata['cultural_backgrounds'] else [],
                    languages=metadata['languages'].split('|') if metadata['languages'] else [],
                    key_concerns=metadata['key_concerns'].split('|') if metadata['key_concerns'] else [],
                    strengths=metadata['strengths'].split('|') if metadata['strengths'] else [],
                    cultural_values=json.loads(metadata['cultural_values']) if metadata['cultural_values'] else {},
                    communication_preferences=json.loads(metadata['communication_preferences']) if metadata['communication_preferences'] else {},
                    created_at=metadata['created_at']
                )
                profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            print(f"Error in advanced community profiles: {e}")
            return []
    
    def _get_community_profiles_fallback(self, community_context: Optional[str] = None) -> List[CommunityProfile]:
        """Get community profiles using fallback method"""
        results = []
        for profile in self.community_profiles:
            if not community_context or profile.community_name == community_context:
                results.append(profile)
        return results
    
    def _extract_cultural_context(self, knowledge_items: List[CulturalKnowledgeItem], 
                                cultural_guidelines: List[CulturalGuideline]) -> str:
        """Extract cultural context from knowledge items and guidelines"""
        context_parts = []
        
        # Extract from knowledge items
        for item in knowledge_items:
            if item.cultural_context:
                context_parts.append(item.cultural_context)
        
        # Extract from cultural guidelines
        for guideline in cultural_guidelines:
            context_parts.extend(guideline.guidelines[:3])  # Top 3 guidelines
        
        return " ".join(context_parts) if context_parts else ""
    
    def _load_existing_data(self):
        """Load existing data for fallback system"""
        try:
            # Load knowledge items
            knowledge_dir = os.path.join(self.data_dir, "knowledge")
            for filename in os.listdir(knowledge_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(knowledge_dir, filename), 'r') as f:
                        data = json.load(f)
                        self.knowledge_items.append(CulturalKnowledgeItem(**data))
            
            # Load cultural guidelines
            cultural_dir = os.path.join(self.data_dir, "cultural")
            for filename in os.listdir(cultural_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(cultural_dir, filename), 'r') as f:
                        data = json.load(f)
                        self.cultural_guidelines.append(CulturalGuideline(**data))
            
            # Load community profiles
            community_dir = os.path.join(self.data_dir, "communities")
            for filename in os.listdir(community_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(community_dir, filename), 'r') as f:
                        data = json.load(f)
                        self.community_profiles.append(CommunityProfile(**data))
                        
        except Exception as e:
            print(f"Error loading existing data: {e}")

# Initialize the advanced RAG system
advanced_rag_db = AdvancedRAGSystem() 