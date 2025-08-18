import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL

def send_email(to_email, subject, body):
    try:
        message = MIMEMultipart()
        message['From'] = FROM_EMAIL
        message['To'] = to_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, message.as_string())

        return True, None
    except Exception as e:
        return False, str(e)

def get_email_template(notification_type, user_name, due_date=None, amount=None):
    if notification_type == 'credit_request_confirmation':
        return (f"Dear {user_name},\n\n"
                "Your credit request has been approved and credited to your account.\n\n"
                "Thank you,\nKhatabook Team")
    elif notification_type == 'overdue_alert':
        return (f"Dear {user_name},\n\n"
                f"Your credit due on {due_date} is overdue. Please settle the amount of {amount} immediately.\n\n"
                "Thank you,\nKhatabook Team")
    elif notification_type == 'bad_debt_warning':
        return (f"Dear {user_name},\n\n"
                f"You have bad debt flagged due to unpaid credits for over 60 days or more.\n"
                "Please contact us immediately to resolve this issue.\n\n"
                "Thank you,\nKhatabook Team")
    else:
        return "Notification from Khatabook."

