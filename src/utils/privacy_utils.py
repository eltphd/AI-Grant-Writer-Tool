"""
This module provides utility functions for data privacy, including the
redaction of Personally Identifiable Information (PII) from text.
"""

import re
from typing import List, Tuple

# Regex patterns for common PII
# Note: These are basic patterns and may not cover all edge cases.
PII_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE": re.compile(r"\b(?:\+?1[ -]?)?\(?([2-9][0-8][0-9])\)?[ -]?([2-9][0-9]{2})[ -]?([0-9]{4})\b"),
    # A simple pattern for names (Title Case words) - this is prone to false positives
    # and should be used with caution or replaced with a more robust NLP approach.
    "NAME": re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b")
}

class PiiRedactor:
    """
    A service to find and redact PII in a given text.
    """

    def redact_text(self, text: str) -> Tuple[str, List[dict]]:
        """
        Redacts PII from the given text and returns the redacted text
        along with a list of the redactions made.

        Args:
            text: The input string to redact.

        Returns:
            A tuple containing:
            - The redacted text.
            - A list of dictionaries, where each dictionary details a redaction
              (original value, type, start index).
        """
        redacted_text = text
        redactions = []

        for pii_type, pattern in PII_PATTERNS.items():
            matches = pattern.finditer(redacted_text)
            for match in matches:
                original_value = match.group(0)
                start_index = match.start()
                end_index = match.end()
                
                # Create a placeholder like [REDACTED_EMAIL]
                placeholder = f"[REDACTED_{pii_type}]"
                
                # Replace the found PII with the placeholder
                redacted_text = redacted_text[:start_index] + placeholder + redacted_text[end_index:]

                redactions.append({
                    "original_value": original_value,
                    "pii_type": pii_type,
                    "start": start_index,
                    "end": end_index
                })
        
        return redacted_text, redactions

# Make an instance available for import
pii_redactor = PiiRedactor()