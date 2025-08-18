# Khatabook Auto Reminder System

## Overview

The Khatabook Auto Reminder System is like a *digital ledger* that helps track money owed and borrowed. Its main purpose is to **automatically send email reminders** to people when their credit payments are due or overdue, preventing bad debt. You can also use it to *manage users*, *record credit transactions*, and *generate reports* through a simple command-line interface.

## Visual Overview

```mermaid
flowchart TD
    A0["System Configuration
"]
    A1["Data Persistence Layer
"]
    A2["Core Business Entities
"]
    A3["Email Notification Service
"]
    A4["Automated Reminder Scheduler
"]
    A5["Command-Line Interface (CLI)
"]
    A1 -- "Reads config" --> A0
    A2 -- "Reads config" --> A0
    A3 -- "Reads config" --> A0
    A4 -- "Reads config" --> A0
    A5 -- "Reads config" --> A0
    A2 -- "Manages data" --> A1
    A5 -- "Manages database" --> A1
    A2 -- "Sends emails" --> A3
    A4 -- "Processes entities" --> A2
    A4 -- "Sends alerts" --> A3
    A5 -- "Operates on entities" --> A2
    A5 -- "Triggers reminders" --> A4
```

## Features

- **User Management:** Add, update, delete users with credit limits.
- **Credit Management:** User credit requests with limit checks.
- **Overdue Alerts:** Reminder emails 7 days before, on due date, 7 days after.
- **Bad Debt Prevention:** Flags users with unpaid credits over 60 days.
- **Email Notifications:** Uses SMTP for notification emails.
- **Database:** SQLite for data persistence with backup.
- **Testing:** Unit tests for core functionality.

## Setup Instructions

1. Install Python 3.x.

2. Install dependencies (if any).

3. Configure `config.py` with your email SMTP credentials.

4. Run the program:


