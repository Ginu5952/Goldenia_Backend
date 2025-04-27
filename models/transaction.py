from models.user import db
from datetime import datetime, timezone

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # top_up, exchange, transfer
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    currency_symbol = db.Column(db.String(5), nullable=False)
    currency_from = db.Column(db.String(3), nullable=True)
    currency_to = db.Column(db.String(3), nullable=True)
    converted_amount = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    target_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    user = db.relationship("User", back_populates="transactions", foreign_keys=[user_id])

    target_user = db.relationship("User", back_populates="received_transactions", foreign_keys=[target_user_id])


    def __repr__(self):
        return f"<Transaction {self.type} {self.amount}{self.currency_symbol} by User {self.user_id}>"
