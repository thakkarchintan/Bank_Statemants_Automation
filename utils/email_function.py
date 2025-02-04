import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(feedback,user_email,ADMIN_EMAILS,SMTP_SERVER,SMTP_USER,SMTP_PASSWORD):
    SMTP_PORT = 587

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(ADMIN_EMAILS)  # Multiple recipients
    msg["Subject"] = "New User Feedback"

    body = f"User Feedback:\n\n{feedback}\n\nFrom: {user_email if user_email else 'Anonymous'}"
    msg.attach(MIMEText(body, "plain"))

    # Send email via SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, ADMIN_EMAILS, msg.as_string())  # Sending to multiple admins
    server.quit()