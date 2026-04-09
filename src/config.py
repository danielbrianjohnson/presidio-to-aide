"""Configuration constants for the ticket sanitizer."""

# Default paths
DEFAULT_INPUT_FILE = "ticket.txt"
DEFAULT_OUTPUT_DIR = "output"
SANITIZED_FILENAME = "sanitized_ticket.txt"
FINDINGS_FILENAME = "findings.json"

# Protegrity Developer Edition settings
PROTEGRITY_ENDPOINT_URL = (
    "http://localhost:8580/pty/data-discovery/v1.1/classify"
)
PROTEGRITY_ENTITY_MAP = {
    "PERSON": "PERSON",
    "LOCATION": "LOCATION",
    "SOCIAL_SECURITY_ID": "SSN",
    "PHONE_NUMBER": "PHONE",
    "EMAIL_ADDRESS": "EMAIL",
    "CREDIT_CARD_NUMBER": "CREDIT_CARD",
    "CREDIT_CARD": "CREDIT_CARD",
    "ACCOUNT_NUMBER": "ACCOUNT_NUMBER",
    "HEALTH_CARE_ID": "ID",
    "AGE": "AGE",
    "USERNAME": "USERNAME",
}
PROTEGRITY_SCORE_THRESHOLD = 0.5
