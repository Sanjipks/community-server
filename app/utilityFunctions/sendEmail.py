from email.message import EmailMessage
from email.utils import make_msgid
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 


import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.image import MIMEImage

def send_authcode_via_email(email: str, authcode: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Verification Code"
    msg["From"] = formataddr(("MyApp", "donotreply@communitynepal.com"))
    msg["To"] = email

    # logo_cid = make_msgid(domain="local")         # e.g. "<p2x9...@local>"
    # logo_token = logo_cid[1:-1]  

    # HTML email content with inline styling and image reference
    html_content = f"""
   
<html lang="en" style="margin:0; padding:0;">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Your Verification Code</title>
  </head>
  <body style="margin:0; padding:0; background:#F2F4F7; font-family:Arial,Helvetica,sans-serif;">
    <!-- Preheader (hidden in most clients) -->
    <div style="display:none; max-height:0; overflow:hidden; opacity:0; color:transparent;">
      Your verification code is inside. It expires in 10 minutes.
    </div>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#F2F4F7;">
      <tr>
        <td align="center" style="padding:24px 16px;">
          <!--[if mso]>
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600">
          <tr><td>
          <![endif]-->
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:600px; background:#FFFFFF; border-radius:12px; border:1px solid #EAECF0;">
            <!-- Header -->
            <tr>
              <td align="center" style="padding:24px 24px 8px;">
                <img src="cid:logo_image" height="64" alt="Company logo" style="display:block; border:0; outline:none; text-decoration:none; width:64px; height:64px; border-radius:12px;" />
                <div style="font-size:14px; color:#667085; margin-top:8px;">Secure verification</div>
              </td>
            </tr>

            <!-- Title -->
            <tr>
              <td align="left" style="padding:8px 24px 0;">
                <h1 style="margin:0; font-size:22px; line-height:30px; color:#101828; font-weight:700;">
                  Your Verification Code
                </h1>
              </td>
            </tr>

            <!-- Intro copy -->
            <tr>
              <td align="left" style="padding:8px 24px 0;">
                <p style="margin:0; font-size:14px; line-height:22px; color:#344054;">
                  Use the code below to verify your account. This code expires in <strong>10 minutes</strong>.
                </p>
              </td>
            </tr>

            <!-- Code block -->
            <tr>
              <td align="center" style="padding:20px 24px 8px;">
                <div style="
                  display:inline-block;
                  background:#0044cc;
                  color:#ffffff;
                  padding:16px 24px;
                  border-radius:10px;
                  font-size:28px;
                  line-height:32px;
                  font-weight:700;
                  letter-spacing:6px;
                  text-align:center;
                  font-family:SFMono-Regular,Menlo,Consolas,Monaco,monospace;">
                  {authcode}
                </div>
              </td>
            </tr>

            <!-- Optional: verify button (if you have a link) -->
            <tr>
              <td align="center" style="padding:16px 24px 0;">
                <!-- Bulletproof-ish button -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td align="center" bgcolor="#0044cc" style="border-radius:8px;">
                      <a href=""
                         style="display:inline-block; padding:12px 18px; font-size:14px; font-weight:600; color:#ffffff; text-decoration:none; border-radius:8px;">
                        Verify my account
                      </a>
                    </td>
                  </tr>
                </table>
                <div style="font-size:12px; color:#667085; margin-top:10px;">
                  If the button doesn’t work, copy and paste this URL into your browser:<br />
                  <span style="word-break:break-all; color:#0044cc;"></span>
                </div>
              </td>
            </tr>

            <!-- Divider -->
            <tr>
              <td style="padding:24px;">
                <hr style="border:none; border-top:1px solid #EAECF0; margin:0;" />
              </td>
            </tr>

            <!-- Help / footer copy -->
            <tr>
              <td align="left" style="padding:0 24px 8px;">
                <p style="margin:0; font-size:13px; line-height:20px; color:#475467;">
                  Didn’t request this code? You can safely ignore this email. Your account remains secure.
                </p>
              </td>
            </tr>
            <tr>
              <td align="left" style="padding:0 24px 24px;">
                <p style="margin:0; font-size:13px; line-height:20px; color:#475467;">
                  Need help? Reply to this email or visit our <a href="" style="color:#0044cc; text-decoration:none;">Help Center</a>.
                </p>
              </td>
            </tr>
          </table>
          <!--[if mso]></td></tr></table><![endif]-->

          <!-- Brand footer -->
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:600px;">
            <tr>
              <td align="center" style="padding:16px 8px;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#98A2B3;">
                  ©Community Nepal. All rights reserved.
                </p>
              </td>
            </tr>
          </table>

        </td>
      </tr>
    </table>
  </body>
</html>

    """

    msg.set_content("Your verification code is: {authcode}")  # Fallback plain-text
    msg.add_alternative(html_content, subtype="html")

    # Attach image (make sure 'logo.png' exists in your project folder)
    try:
        with open("images/logo.svg", "rb") as img:
            msg.get_payload()[1].add_related(img.read(), "image", "svg", cid="logo_image")
    except FileNotFoundError:
        print("⚠️ logo.svg not found — sending email without image.")

    # Send via Gmail
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
