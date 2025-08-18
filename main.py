import sys
from models import User
from db import setup_database
from scheduler import send_due_reminders
from config import BACKUP_PATH
from db import backup_database

def print_menu():
    print("\nKhatabook Auto Reminder System")
    print("1. Add User")
    print("2. Update User")
    print("3. Delete User")
    print("4. Request Credit")
    print("5. Pay Credit")
    print("6. Send Due Reminders")
    print("7. Generate Reports")
    print("8. Backup Database")
    print("9. Exit")

def main():
    setup_database()

    while True:
        print_menu()
        choice = input("Select option: ").strip()

        if choice == '1':
            name = input("Enter name: ")
            email = input("Enter email: ")
            max_limit = float(input("Enter max credit limit: "))
            try:
                user_id = User.add_user(name, email, max_limit)
                print(f"User added with ID: {user_id}")
            except Exception as e:
                print(f"Error adding user: {e}")

        elif choice == '2':
            user_id = int(input("Enter user ID to update: "))
            user = User.get_user_by_id(user_id)
            if not user:
                print("User not found")
                continue
            print("Leave blank to skip update")
            name = input(f"Name ({user.name}): ") or None
            email = input(f"Email ({user.email}): ") or None
            max_limit_str = input(f"Max Credit Limit ({user.max_credit_limit}): ")
            max_limit = float(max_limit_str) if max_limit_str else None

            try:
                user.update(name, email, max_limit)
                print("User updated")
            except Exception as e:
                print(f"Error updating user: {e}")

        elif choice == '3':
            user_id = int(input("Enter user ID to delete: "))
            user = User.get_user_by_id(user_id)
            if not user:
                print("User not found")
                continue
            user.delete()
            print("User deleted")

        elif choice == '4':
            user_id = int(input("Enter user ID to request credit: "))
            user = User.get_user_by_id(user_id)
            if not user:
                print("User not found")
                continue
            amount = float(input("Enter credit amount: "))
            try:
                credit_id = user.request_credit(amount)
                print(f"Credit granted with ID {credit_id}")
            except Exception as e:
                print(f"Credit request failed: {e}")

        elif choice == '5':
            user_id = int(input("Enter user ID: "))
            user = User.get_user_by_id(user_id)
            if not user:
                print("User not found")
                continue
            credit_id = int(input("Enter credit ID to pay: "))
            try:
                user.pay_credit(credit_id)
                print("Credit paid successfully")
            except Exception as e:
                print(f"Payment failed: {e}")

        elif choice == '6':
            print("Sending due reminders...")
            send_due_reminders()
            print("Reminders sent")

        elif choice == '7':
            from models import NotificationLog
            print("\nOverdue Accounts:")
            overdue_report = NotificationLog.generate_overdue_report()
            for name, email, amount, due_date in overdue_report:
                print(f"{name} ({email}) - Amount: {amount}, Due Date: {due_date}")

            print("\nBad Debt Accounts:")
            bad_debt_report = NotificationLog.generate_bad_debt_report()
            for name, email, balance in bad_debt_report:
                print(f"{name} ({email}) - Balance: {balance}")

        elif choice == '8':
            try:
                backup_database(BACKUP_PATH)
                print(f"Database backed up to {BACKUP_PATH}")
            except Exception as e:
                print(f"Backup failed: {e}")

        elif choice == '9':
            print("Exiting...")
            sys.exit(0)

        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()


