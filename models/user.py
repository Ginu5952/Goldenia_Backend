from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(180), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    currency = db.Column(db.String(3), default="USD")
    
    # Transactions initiated by the user
    transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.user_id',
        back_populates='user',
        lazy=True
    )

    # Transactions where this user was the recipient
    received_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.target_user_id',
        back_populates='target_user',
        lazy=True
    )

    balances = db.relationship("UserBalance", back_populates="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
    
  
    
