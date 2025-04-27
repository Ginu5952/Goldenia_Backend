import unittest
from tests.base_test import BaseTestCase
from models.user import User
from models.user_balance import UserBalance
from app import db

class TransferTestCase(BaseTestCase):

    def test_successful_transfer(self):
        """Test successful money transfer"""
        
        sender_data = {
            "username": "sender",
            "email": "sender@example.com",
            "password": "password123"
        }
        response = self.client.post('/auth/signup', json=sender_data)
        self.assertEqual(response.status_code, 201)
        login_data = {"email": "sender@example.com", "password": "password123"}
        response = self.client.post('/auth/login', json=login_data)
        token_sender = response.get_json()['access_token']

        receiver_data = {
            "username": "receiver",
            "email": "receiver@example.com",
            "password": "password123"
        }
        response = self.client.post('/auth/signup', json=receiver_data)
        self.assertEqual(response.status_code, 201)
        login_data = {"email": "receiver@example.com", "password": "password123"}
        response = self.client.post('/auth/login', json=login_data)
        token_receiver = response.get_json()['access_token']

        with self.app.app_context():
            sender = User.query.filter_by(username="sender").first()
            receiver = User.query.filter_by(username="receiver").first()

            sender_balance = UserBalance(user_id=sender.id, currency="USD", balance=100.0)
            receiver_balance = UserBalance(user_id=receiver.id, currency="USD", balance=50.0)

            db.session.add(sender_balance)
            db.session.add(receiver_balance)
            db.session.commit()

            receiver_id = receiver.id


        # Transfer money from sender to receiver
        transfer_data = {
            "target_user_id": receiver_id,   
            "amount": 30,                    
            "currency": "USD" 
        }
        response = self.client.post('/user/transfer', 
                                    json=transfer_data,
                                    headers={"Authorization": f"Bearer {token_sender}"})
        
        print(response.status_code)
        print(response.get_json())
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            sender = User.query.filter_by(username="sender").first()
            receiver = User.query.filter_by(username="receiver").first()
            sender_balance = sender.balances[0].balance
            receiver_balance = receiver.balances[0].balance

            self.assertEqual(sender_balance, 70)
            self.assertEqual(receiver_balance, 80)

    def test_transfer_insufficient_balance(self):
        """Test transfer fails when sender has insufficient balance"""
        
       
        sender_data = {
            "username": "lowbalance",
            "email": "lowbalance@example.com",
            "password": "password123"
        }
        response = self.client.post('/auth/signup', json=sender_data)
        self.assertEqual(response.status_code, 201)
        login_data = {"email": "lowbalance@example.com", "password": "password123"}
        response = self.client.post('/auth/login', json=login_data)
        token_sender = response.get_json()['access_token']

        receiver_data = {
            "username": "richuser",
            "email": "richuser@example.com",
            "password": "password123"
        }
        response = self.client.post('/auth/signup', json=receiver_data)
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():
            sender = User.query.filter_by(username="lowbalance").first()
            receiver = User.query.filter_by(username="richuser").first()

            # Set up balances manually
            sender_balance = UserBalance(user_id=sender.id, currency="USD", balance=10.0)  # Small balance
            receiver_balance = UserBalance(user_id=receiver.id, currency="USD", balance=50.0)

            db.session.add(sender_balance)
            db.session.add(receiver_balance)
            db.session.commit()

            receiver_id = receiver.id 

        # Try to transfer too much
        transfer_data = {
            "target_user_id": receiver_id,
            "amount": 1000,  
            "currency": "USD"
        }
        response = self.client.post('/user/transfer',
                                    json=transfer_data,
                                    headers={"Authorization": f"Bearer {token_sender}"})
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], "Insufficient balance")


if __name__ == '__main__':
    unittest.main()
