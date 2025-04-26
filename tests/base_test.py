import unittest
from app import create_app, db
from models import User, UserBalance
from flask_jwt_extended import create_access_token

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run once for the whole test class."""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests."""
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()