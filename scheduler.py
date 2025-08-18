import datetime
from models import User, NotificationLog
from email_service import send_email, get_email_template
from config import REMINDER_DAYS_BEFORE, REMINDER_DAYS_AFTER, CREDIT_DUE_DAYS

DATE_FORMAT = "%Y-%m-%d"

def send_due_reminders():
    today = datetime.date.today()

    users = User.list_all_users()

    for user in users:
        with get_connection() as conn:
            cur = conn.cursor()
            # Get credits that are due
            cur.execute("""
                SELECT id, amount, due_date, paid, overdue FROM credits
                WHERE user_id = ? AND paid = 0
            """, (user.id,))
            credits = cur.fetchall()

        for credit in credits:
            credit_id, amount, due_date_str, paid, overdue = credit
            due_date = datetime.datetime.strptime(due_date_str, DATE_FORMAT).date()

            # Calculate days difference
            days_diff = (due_date - today).days

            # Send reminders:
            # 7 days before due date
            if days_diff == REMINDER_DAYS_BEFORE:
                send_notification(user, credit_id, 'overdue_alert', due_date_str, amount)

            # On due date
            elif days_diff == 0:
                send_notification(user, credit_id, 'overdue_alert', due_date_str, amount)

            # 7 days after due date and credit not paid -> overdue alert, mark overdue
            elif days_diff == -REMINDER_DAYS_AFTER:
                # Mark credit overdue if not done already
                if overdue == 0:
                    user.mark_overdue_credits()
                send_notification(user, credit_id,'overdue_alert', due_date_str, amount)

        # Check and flag bad debt
        bad_debt_flag = user.flag_bad_debt()
        if bad_debt_flag:
            # Send bad debt warning email
            subject = "Bad Debt Warning"
            body = get_email_template('bad_debt_warning', user.name)
            success, error = send_email(user.email, subject, body)
            NotificationLog.log_notification(user.id, 'bad_debt_warning', status='sent' if success else f'failed: {error}')

def send_notification(user, credit_id, notification_type, due_date, amount):
    subject = "Credit Overdue Alert"
    body = get_email_template(notification_type, user.name, due_date, amount)
    success, error = send_email(user.email, subject, body)
    NotificationLog.log_notification(user.id, notification_type, credit_id, status='sent' if success else f'failed: {error}')

