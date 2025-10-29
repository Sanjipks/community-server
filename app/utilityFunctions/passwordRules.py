import re

def check_password(password: str):
    # check minimum length
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    # check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # check for at least one lowercase letter
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    # check for at least one digit
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    
    # check for at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    
    # check for prohibited patterns
    prohibited_patterns = ["123456", "password", "qwerty"]
    if any(pattern in password.lower() for pattern in prohibited_patterns):
        raise ValueError("Password contains prohibited patterns")
    
    # if all checks pass, return True
    return True