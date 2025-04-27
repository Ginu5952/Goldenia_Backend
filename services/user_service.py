
from utils.utils import get_currency_symbol 
from flask import jsonify

class UserService:

    @staticmethod
    def get_user_profile(user):

        if not user:
            return jsonify({"message": "User not found"}), 404


        balances = [
            {
                "currency": balance.currency,
                "amount": round(balance.balance, 2),
                "symbol": get_currency_symbol(balance.currency)
            }
            for balance in user.balances
        ]

        return {
            "id": user.id,
            "username": user.username,
            "balances": balances
        }