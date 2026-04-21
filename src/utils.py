"""Helper utilities."""

import re

def sanitize_identifier(name: str) -> str:
    """Convert to valid C identifier."""
    return re.sub(r'\W|^(?=\d)', '_', name)