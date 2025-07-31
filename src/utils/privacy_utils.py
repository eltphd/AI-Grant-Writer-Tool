"""Privacy utilities for automatic PII detection and redaction.

This module provides functions for detecting and redacting sensitive information
while maintaining data utility for AI processing.
"""

import re
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import spacy
from dataclasses import dataclass
import uuid

# Try to load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    print("⚠️ spaCy model not available. Install with: python -m spacy download en_core_web_sm")
    SPACY_AVAILABLE = False

@dataclass
class SensitiveEntity:
    """Represents a detected sensitive entity."""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    redacted_text: str
    hash_id: str

class PrivacyDetector:
    """Detects and redacts sensitive information."""
    
    def __init__(self):
        self.patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'ssn_alt': r'\b\d{9}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'government_id': r'\b[A-Z]{2}\d{6,8}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'date_of_birth': r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'mac_address': r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b',
            'url': r'\bhttps?://[^\s<>"]+|www\.[^\s<>"]+\b',
            'bank_account': r'\b\d{8,17}\b',  # Basic pattern, may need refinement
        }
        
        self.entity_types = {
            'ssn': 'SOCIAL_SECURITY_NUMBER',
            'ssn_alt': 'SOCIAL_SECURITY_NUMBER',
            'phone': 'PHONE_NUMBER',
            'email': 'EMAIL_ADDRESS',
            'credit_card': 'CREDIT_CARD_NUMBER',
            'government_id': 'GOVERNMENT_ID',
            'address': 'ADDRESS',
            'zip_code': 'ZIP_CODE',
            'date_of_birth': 'DATE_OF_BIRTH',
            'ip_address': 'IP_ADDRESS',
            'mac_address': 'MAC_ADDRESS',
            'url': 'URL',
            'bank_account': 'BANK_ACCOUNT_NUMBER'
        }
    
    def detect_sensitive_data(self, text: str) -> List[SensitiveEntity]:
        """Detect sensitive entities in text using regex patterns and NER."""
        entities = []
        
        # Pattern-based detection
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = self._create_entity(
                    text=match.group(),
                    entity_type=self.entity_types.get(pattern_name, pattern_name.upper()),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9
                )
                entities.append(entity)
        
        # NER-based detection for names and organizations
        if SPACY_AVAILABLE:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                    # Check if this entity wasn't already detected by patterns
                    if not any(e.start_pos <= ent.start_char < e.end_pos for e in entities):
                        entity = self._create_entity(
                            text=ent.text,
                            entity_type=f"NAMED_{ent.label_}",
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            confidence=0.8
                        )
                        entities.append(entity)
        
        # Remove overlapping entities (keep the one with higher confidence)
        entities = self._remove_overlapping_entities(entities)
        
        return entities
    
    def _create_entity(self, text: str, entity_type: str, start_pos: int, end_pos: int, confidence: float) -> SensitiveEntity:
        """Create a SensitiveEntity with redacted text and hash."""
        hash_id = hashlib.sha256(text.encode()).hexdigest()
        redacted_text = self._generate_redacted_text(text, entity_type)
        
        return SensitiveEntity(
            text=text,
            entity_type=entity_type,
            start_pos=start_pos,
            end_pos=end_pos,
            confidence=confidence,
            redacted_text=redacted_text,
            hash_id=hash_id
        )
    
    def _generate_redacted_text(self, text: str, entity_type: str) -> str:
        """Generate redacted version of sensitive text."""
        if entity_type == 'SOCIAL_SECURITY_NUMBER':
            return f"[REDACTED_SSN_{text[-4:]}]"
        elif entity_type == 'PHONE_NUMBER':
            return f"[REDACTED_PHONE_{text[-4:]}]"
        elif entity_type == 'EMAIL_ADDRESS':
            parts = text.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
            return "[REDACTED_EMAIL]"
        elif entity_type == 'CREDIT_CARD_NUMBER':
            return f"[REDACTED_CC_{text[-4:]}]"
        elif entity_type == 'GOVERNMENT_ID':
            return f"[REDACTED_GOV_ID_{text[-3:]}]"
        elif entity_type == 'BANK_ACCOUNT_NUMBER':
            return f"[REDACTED_BANK_{text[-4:]}]"
        elif entity_type.startswith('NAMED_'):
            return f"[REDACTED_{entity_type.split('_')[1]}]"
        else:
            return f"[REDACTED_{entity_type}]"
    
    def _remove_overlapping_entities(self, entities: List[SensitiveEntity]) -> List[SensitiveEntity]:
        """Remove overlapping entities, keeping the one with higher confidence."""
        if not entities:
            return entities
        
        # Sort by confidence (descending) and start position
        entities.sort(key=lambda x: (-x.confidence, x.start_pos))
        
        filtered = []
        for entity in entities:
            # Check if this entity overlaps with any already accepted entity
            overlaps = False
            for accepted in filtered:
                if (entity.start_pos < accepted.end_pos and 
                    entity.end_pos > accepted.start_pos):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered
    
    def redact_text(self, text: str) -> Tuple[str, List[SensitiveEntity]]:
        """Redact sensitive entities from text and return redacted text with entities."""
        entities = self.detect_sensitive_data(text)
        
        # Sort entities by start position (descending) to avoid position shifts
        entities.sort(key=lambda x: x.start_pos, reverse=True)
        
        redacted_text = text
        for entity in entities:
            redacted_text = (
                redacted_text[:entity.start_pos] + 
                entity.redacted_text + 
                redacted_text[entity.end_pos:]
            )
        
        return redacted_text, entities

class PrivacyManager:
    """Manages privacy-compliant data storage and retrieval."""
    
    def __init__(self):
        self.detector = PrivacyDetector()
    
    def process_text_for_storage(self, text: str, project_id: str, content_type: str = "text") -> Dict[str, Any]:
        """Process text for privacy-compliant storage."""
        # Detect and redact sensitive data
        redacted_text, entities = self.detector.redact_text(text)
        
        # Create storage record
        storage_record = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "content_type": content_type,
            "original_text": text,
            "redacted_text": redacted_text,
            "entities": [
                {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos,
                    "confidence": entity.confidence,
                    "redacted_text": entity.redacted_text,
                    "hash_id": entity.hash_id
                }
                for entity in entities
            ],
            "created_at": datetime.now().isoformat(),
            "privacy_level": "high" if entities else "low"
        }
        
        return storage_record
    
    def get_safe_text_for_ai(self, storage_record: Dict[str, Any]) -> str:
        """Get privacy-safe text for AI processing."""
        return storage_record.get("redacted_text", storage_record.get("original_text", ""))
    
    def get_original_text(self, storage_record: Dict[str, Any], require_auth: bool = True) -> Optional[str]:
        """Get original text (requires authentication in production)."""
        if require_auth:  # In production, check user permissions here
            return storage_record.get("original_text")
        return None
    
    def create_embedding_context(self, storage_records: List[Dict[str, Any]]) -> str:
        """Create embedding context from privacy-safe records."""
        safe_texts = []
        for record in storage_records:
            safe_text = self.get_safe_text_for_ai(record)
            if safe_text:
                safe_texts.append(safe_text)
        
        return "\n\n".join(safe_texts)
    
    def audit_privacy_compliance(self, project_id: str, storage_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit privacy compliance for a project."""
        total_entities = 0
        entity_types = {}
        
        for record in storage_records:
            entities = record.get("entities", [])
            total_entities += len(entities)
            
            for entity in entities:
                entity_type = entity.get("entity_type", "UNKNOWN")
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        return {
            "project_id": project_id,
            "total_records": len(storage_records),
            "total_entities_detected": total_entities,
            "entity_type_breakdown": entity_types,
            "compliance_status": "compliant" if total_entities > 0 else "no_sensitive_data",
            "audit_timestamp": datetime.now().isoformat()
        }

# Global instance
privacy_manager = PrivacyManager() 