def check_password(password: str) -> bool:
    """
    Check if the password meets the specified rules:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character

    :param password: The password to check
    :return: True if the password meets all rules, False otherwise
    """
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for c in password)

    return has_upper and has_lower and has_digit and has_special    