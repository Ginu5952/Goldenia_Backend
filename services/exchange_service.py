from models.user import db
from models.user_balance import UserBalance
from models.transaction import Transaction
from flask import jsonify
from utils.utils import get_currency_symbol 

class ExchangeService:

    @staticmethod
    def exchange(user,amount, currency_from,  currency_to ):
         
        if not user:
            return {"message": "User not found"}, 404

    
        if not amount or amount <= 0:
            return {"status": "error","message": "Amount must be greater than zero"}, 400
        if currency_from == currency_to:
            return {"status": "error", "message": "Currencies must be different"}, 400

        exchange_rates = {
            ("USD", "EUR"): 0.87896,
            ("EUR", "USD"): 1.1379,
        }

        rate = exchange_rates.get((currency_from, currency_to))

        if not rate:
            return { "status": "error","message": "Currency pair not supported"}, 400

        balance_from = next((b for b in user.balances if b.currency == currency_from), None)
        balance_to = next((b for b in user.balances if b.currency == currency_to), None)

        if not balance_from or balance_from.balance < amount:
            return {"status": "error", "message": f"Insufficient balance in {currency_from}"}, 400

        if not balance_to:
            balance_to = UserBalance(user_id=user.id, currency=currency_to, balance=0.0)
            db.session.add(balance_to)

        converted_amount = amount * rate
        balance_from.balance -= amount
        balance_to.balance += converted_amount

        transaction = Transaction(
            user_id=user.id,
            type="exchange",
            amount=amount,
            currency_from=currency_from,
            currency_to=currency_to,
            converted_amount=converted_amount,
            currency=currency_from,
            currency_symbol=get_currency_symbol(currency_from)
        )

        db.session.add(transaction)
        db.session.commit()

        user.balance = sum([b.balance for b in user.balances])

        return {
            "message": "Exchange successful",
            "converted_amount": round(converted_amount, 2),
            "balance_from": round(balance_from.balance, 2),
            "balance_to": round(balance_to.balance, 2),
            "currency_from": currency_from,
            "currency_to": currency_to,
            "currency_symbol": get_currency_symbol(currency_to)
        },200


