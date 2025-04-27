import unittest
from tests.base_test import BaseTestCase
from models.user import User
from app import db

class UserTestCase(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create a user once for the entire test class."""
        super().setUpClass()
        with cls.app.app_context():
            user = User(username='paul', email='paul@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

    def test_create_user(self):
        user_data = {
            "username": "john",
            "email": "john@example.com",
            "password": "password123"
        }
        response = self.client.post('/auth/signup', json=user_data)
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        login_data = {
            "email": "paul@example.com",  # This is the user created in setUpClass
            "password": "password123"
        }
        response = self.client.post('/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('access_token', response_data)
        self.assertIn('role', response_data)

if __name__ == '__main__':
    unittest.main()
