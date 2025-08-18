import datetime
from db import get_connection
from email_service import send_email, get_email_template
from config import CREDIT_DUE_DAYS, BAD_DEBT_THRESHOLD_DAYS

DATE_FORMAT = "%Y-%m-%d"


class User:
    def __init__(self, id, name, email, max_credit_limit, current_balance, bad_debt_flag=False):
        self.id = id
        self.name = name
        self.email = email
        self.max_credit_limit = max_credit_limit
        self.current_balance = current_balance
        self.bad_debt_flag = bad_debt_flag

    @staticmethod
    def add_user(name, email, max_credit_limit):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, max_credit_limit, current_balance) VALUES (?, ?, ?, 0)",
                        (name, email.lower(), max_credit_limit))
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def get_user_by_id(user_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, max_credit_limit, current_balance, bad_debt_flag FROM users WHERE id=?",
                        (user_id,))
            row = cur.fetchone()
            if row:
                return User(*row)
            else:
                return None

    @staticmethod
    def get_user_by_email(email):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, max_credit_limit, current_balance, bad_debt_flag FROM users WHERE email=?",
                        (email.lower(),))
            row = cur.fetchone()
            if row:
                return User(*row)
            else:
                return None

    def update(self, name=None, email=None, max_credit_limit=None):
        with get_connection() as conn:
            cur = conn.cursor()
            if name:
                self.name = name
            if email:
                self.email = email.lower()
            if max_credit_limit is not None:
                self.max_credit_limit = max_credit_limit

            cur.execute("""
                UPDATE users SET name=?, email=?, max_credit_limit=?, current_balance=?, bad_debt_flag=?
                WHERE id=?
            """, (self.name, self.email, self.max_credit_limit, self.current_balance,
                  1 if self.bad_debt_flag else 0, self.id))
            conn.commit()

    def delete(self):
        with get_connection() as conn:
            cur = conn.cursor()
            # Delete credits & notifications first to maintain integrity
            cur.execute("DELETE FROM credits WHERE user_id=?", (self.id,))
            cur.execute("DELETE FROM notifications WHERE user_id=?", (self.id,))
            cur.execute("DELETE FROM users WHERE id=?", (self.id,))
            conn.commit()

    def can_request_credit(self, amount):
        return (self.current_balance + amount) <= self.max_credit_limit

    def request_credit(self, amount):
        if not self.can_request_credit(amount):
            raise ValueError(f"Credit request exceeds max credit limit ({self.max_credit_limit})")

        credit_date = datetime.date.today()
        due_date = credit_date + datetime.timedelta(days=CREDIT_DUE_DAYS)

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO credits (user_id, amount, credit_date, due_date, paid, overdue) VALUES (?, ?, ?, ?, 0, 0)",
                        (self.id, amount, credit_date.strftime(DATE_FORMAT), due_date.strftime(DATE_FORMAT)))
            credit_id = cur.lastrowid
            # Update user's current balance
            self.current_balance += amount
            cur.execute("UPDATE users SET current_balance=? WHERE id=?", (self.current_balance, self.id))
            conn.commit()

        # Send confirmation email
        subject = "Credit Request Confirmation"
        body = get_email_template('credit_request_confirmation', self.name)
        send_email(self.email, subject, body)
        return credit_id

    def mark_overdue_credits(self):
        with get_connection() as conn:
            cur = conn.cursor()
            today_str = datetime.date.today().strftime(DATE_FORMAT)
            # Mark overdue if due_date has passed and not paid
            cur.execute("""
                UPDATE credits SET overdue=1 WHERE user_id=? AND overdue=0 AND paid=0 AND due_date < ?
            """, (self.id, today_str))
            conn.commit()

    def get_overdue_credits(self):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, amount, due_date FROM credits WHERE user_id=? AND overdue=1 AND paid=0
            """, (self.id,))
            return cur.fetchall()

    def flag_bad_debt(self):
        # Flag user with bad debt if credits overdue > BAD_DEBT_THRESHOLD_DAYS
        with get_connection() as conn:
            cur = conn.cursor()
            threshold_date = datetime.date.today() - datetime.timedelta(days=BAD_DEBT_THRESHOLD_DAYS)
            threshold_str = threshold_date.strftime(DATE_FORMAT)
            cur.execute("""
                SELECT COUNT(*) FROM credits 
                WHERE user_id=? AND overdue=1 AND paid=0 AND due_date < ?
            """, (self.id, threshold_str))
            count = cur.fetchone()[0]
            if count > 0:
                self.bad_debt_flag = True
            else:
                self.bad_debt_flag = False
            cur.execute("UPDATE users SET bad_debt_flag=? WHERE id=?", (1 if self.bad_debt_flag else 0, self.id))
            conn.commit()
            return self.bad_debt_flag

    def pay_credit(self, credit_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT amount, paid FROM credits WHERE id=? AND user_id=?", (credit_id, self.id))
            row = cur.fetchone()
            if row is None:
                raise ValueError("Credit does not exist or does not belong to user")
            amount, paid = row
            if paid == 1:
                raise ValueError("Credit already paid")

            # Mark credit as paid
            cur.execute("UPDATE credits SET paid=1, overdue=0 WHERE id=?", (credit_id,))
            # Reduce user's current balance
            self.current_balance -= amount
            if self.current_balance < 0:
                self.current_balance = 0
            cur.execute("UPDATE users SET current_balance=? WHERE id=?", (self.current_balance, self.id))
            conn.commit()

    @staticmethod
    def list_all_users():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, max_credit_limit, current_balance, bad_debt_flag FROM users")
            rows = cur.fetchall()
            return [User(*row) for row in rows]

class NotificationLog:

    @staticmethod
    def log_notification(user_id, notification_type, credit_id=None, status="sent"):
        from datetime import datetime
        sent_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO notifications (user_id, credit_id, notification_type, sent_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, credit_id, notification_type, sent_date, status))
            conn.commit()

    @staticmethod
    def generate_overdue_report():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.name, u.email, c.amount, c.due_date
                FROM credits c
                JOIN users u ON c.user_id = u.id
                WHERE c.overdue = 1 AND c.paid=0
            """)
            return cur.fetchall()

    @staticmethod
    def generate_bad_debt_report():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT name, email, current_balance
                FROM users
                WHERE bad_debt_flag = 1
            """)
            return cur.fetchall()


