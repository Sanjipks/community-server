import secrets, string 

# Helper to generate an 8-char, high-entropy code (A-Z, 0-9)
def gen_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))