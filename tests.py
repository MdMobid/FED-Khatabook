import unittest
from models import User
from db import setup_database
import os

class TestUserManagement(unittest.TestCase):
    def setUp(self):
        # Initialize fresh test DB
        if os.path.exists('test_Khatabook.db'):
            os.remove('test_Khatabook.db')
        from config import DB_NAME
        import shutil
        shutil.copyfile(DB_NAME, 'test_Khatabook.db')
        global DB_NAME
        import config
        config.DB_NAME = 'test_Khatabook.db'
        setup_database()

    def tearDown(self):
        try:
            os.remove('test_Khatabook.db')
        except FileNotFoundError:
            pass

    def test_add_user(self):
        user_id = User.add_user("Test User", "testuser@example.com", 1000)
        self.assertIsInstance(user_id, int)

    def test_user_credit_request(self):
        user_id = User.add_user("Credit User", "credituser@example.com", 1000)
        user = User.get_user_by_id(user_id)
        credit_id = user.request_credit(500)
        self.assertIsInstance(credit_id, int)
        self.assertEqual(user.current_balance, 500)

    def test_exceed_credit_limit(self):
        user_id = User.add_user("Limit User", "limituser@example.com", 300)
        user = User.get_user_by_id(user_id)
        with self.assertRaises(ValueError):
            user.request_credit(500)

    def test_pay_credit(self):
        user_id = User.add_user("Pay User", "payuser@example.com", 1000)
        user = User.get_user_by_id(user_id)
        credit_id = user.request_credit(200)
        user.pay_credit(credit_id)
        self.assertEqual(user.current_balance, 0)


if __name__ == '__main__':
    unittest.main()

