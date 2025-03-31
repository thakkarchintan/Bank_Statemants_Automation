import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from constant_variables import *

def send_email(feedback,user_email,uploaded_file):
    SMTP_PORT = 587
    # Admin Email Config
    ADMIN_EMAILS = [ADMIN_EMAIL1, ADMIN_EMAIL2]
    SMTP_PASSWORD = email_pass  # Use an App Password, not your main password
    
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(ADMIN_EMAILS)  # Multiple recipients
    msg["Subject"] = "New User Feedback"

    body = f"User Feedback:\n\n{feedback}\n\nFrom: {user_email if user_email else 'Anonymous'}"
    msg.attach(MIMEText(body, "plain"))

    # Attach file if uploaded
    if uploaded_file:
        file_name = uploaded_file.name
        file_data = uploaded_file.read()
        
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file_data)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={file_name}")
        msg.attach(part)

    # Send email via SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, ADMIN_EMAILS, msg.as_string())  # Sending to multiple admins
    server.quit()

def welcome_email(body,subject,user_email):
    SMTP_PORT = 587
    # Admin Email Config
    ADMIN_EMAILS = [user_email]
    SMTP_PASSWORD = email_pass  # Use an App Password, not your main password
    
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(ADMIN_EMAILS)  # Multiple recipients
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Send email via SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, ADMIN_EMAILS, msg.as_string())  # Sending to multiple admins
    server.quit()

