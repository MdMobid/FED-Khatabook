import sqlite3
from contextlib import closing
from config import DB_NAME

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    with closing(get_connection()) as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            max_credit_limit REAL NOT NULL,
            current_balance REAL NOT NULL DEFAULT 0,
            bad_debt_flag INTEGER DEFAULT 0
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            credit_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0,
            overdue INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            credit_id INTEGER,
            notification_type TEXT NOT NULL,
            sent_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(credit_id) REFERENCES credits(id)
        )''')

        conn.commit()

def backup_database(backup_path):
    with closing(get_connection()) as conn, open(backup_path, 'wb') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n".encode())

