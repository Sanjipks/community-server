import smtplib
from dotenv import load_dotenv
import os
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 


# def send_authcode_via_email(email: str, authcode: str):
#     print('email', email, 'authcode', authcode)
#     with smtplib.SMTP("smtp.gmail.com", 587) as server:
#         server.starttls()
#         server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         server.sendmail(
#             "noreply@email.com",
#             email,
#             f"Subject: Your Verification Code\n\nYour verification code is: {authcode}"
#         )

import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.image import MIMEImage

def send_authcode_via_email(email: str, authcode: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Verification Code"
    msg["From"] = formataddr(("MyApp", EMAIL_ADDRESS))
    msg["To"] = email

    # HTML email content with inline styling and image reference
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <h2 style="color: #333;">Your Verification Code</h2>
        <p>Use the code below to verify your account:</p>
        <div style="text-align: center;background-color: #f9f9f9; width: 474px; height: 800px;">
        <div style="background-color: #0044cc; color: white; padding: 15px; 
                    font-size: 22px; text-align: center; width: 600px; 
                    border-radius: 8px; margin: 20px auto;">
          {authcode}
        </div>
        </div>
        <p>Thank you for using our service!</p>
        <img src="cid:logo_image" alt="Logo" style="width:150px; margin-top:20px;" />
      </body>
    </html>
    """

    msg.set_content("Your verification code is: {authcode}")  # Fallback plain-text
    msg.add_alternative(html_content, subtype="html")

    # Attach image (make sure 'logo.png' exists in your project folder)
    try:
        with open("logo.png", "rb") as img:
            msg.get_payload()[1].add_related(img.read(), "image", "png", cid="logo_image")
    except FileNotFoundError:
        print("⚠️ logo.png not found — sending email without image.")

    # Send via Gmail
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
