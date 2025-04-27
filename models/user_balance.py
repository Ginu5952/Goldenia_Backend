from models.user import db

class UserBalance(db.Model):
    __tablename__ = 'user_balance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="balances")

    def __repr__(self):
        return f"<Balance {self.currency}: {self.balance} for User {self.user_id}>"  