def normalize_email(email: str) -> str:
    """Trim surrounding whitespace and lower-case the email for storage / lookup."""
    return email.strip().lower()
