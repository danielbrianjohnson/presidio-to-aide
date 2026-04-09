"""Configuration constants for the ticket sanitizer."""

# Default paths
DEFAULT_INPUT_FILE = "ticket.txt"
DEFAULT_OUTPUT_DIR = "output"
SANITIZED_FILENAME = "sanitized_ticket.txt"
FINDINGS_FILENAME = "findings.json"

# Presidio settings
PRESIDIO_LANGUAGE = "en"
PRESIDIO_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "US_SSN",
    "CREDIT_CARD",
]

# Anonymization placeholder template — uses angle brackets for clarity in demos
ANON_PLACEHOLDER = "<{entity_type}>"
