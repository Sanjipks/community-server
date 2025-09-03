import smtplib
from dotenv import load_dotenv
import os
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 


def send_authcode_via_email(email: str, authcode: str):
    print('email', email, 'authcode', authcode)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(
            "noreply@email.com",
            email,
            f"Subject: Your Verification Code\n\nYour verification code is: {authcode}"
        )

