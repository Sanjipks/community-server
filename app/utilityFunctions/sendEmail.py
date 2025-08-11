import smtplib

def send_authcode_via_email(email: str, authcode: str):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_email@gmail.com", "your_password")
        server.sendmail(
            "noreply@email.com",
            email,
            f"Subject: Your Verification Code\n\nYour verification code is: {authcode}"
        )

