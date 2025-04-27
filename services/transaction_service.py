# services/transaction_service.py
from models.user import db, User
from models.user_balance import UserBalance
from models.transaction import Transaction
from datetime import datetime
from flask import jsonify
from utils.utils import get_currency_symbol 

class TransactionService:

    @staticmethod
    def top_up(identity, amount):

        user = User.query.get(int(identity))

        if not user:
         return jsonify({"error": "User not found"}), 404

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400
       
        currency = user.currency  

        user_balance = UserBalance.query.filter_by(user_id=user.id, currency=currency).first()
        
        if not user_balance:
            user_balance = UserBalance(user_id=user.id, currency=user.currency, balance=0.0)
            db.session.add(user_balance)

        user_balance.balance += amount

        transaction = Transaction(
            user_id=user.id,
            type="top_up",
            amount=amount,
            currency=user.currency,
            currency_symbol="$",
            created_at=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()

        return {
            "balance": round(user_balance.balance, 2),
            "currency_symbol": "$",
            "message": "Top-up successful",
        },200

    @staticmethod
    def transfer(current_user_id, target_user_id, amount, currency):

   
        if not all([amount, target_user_id, currency]):
            return {"message": "Amount, target_user_id, and currency are required"}, 400
        if amount <= 0:
            return {"message": "Amount must be greater than 0"}, 400

        # current_user = User.query.get(current_user_id)
        # target_user = User.query.get(target_user_id)

        current_user = db.session.get(User, current_user_id)
        target_user = db.session.get(User, target_user_id)


        if not current_user or not target_user:
            return {"message": "User not found"}, 404

    
        sender_balance = UserBalance.query.filter_by(user_id=current_user.id, currency=currency).first()
        receiver_balance = UserBalance.query.filter_by(user_id=target_user.id, currency=currency).first()

        if not sender_balance or sender_balance.balance < amount:
            return {"message": f"Insufficient balance in {currency}"}, 400

    
        if not receiver_balance:
            receiver_balance = UserBalance(user_id=target_user.id, currency=currency, balance=0.0)
            db.session.add(receiver_balance)

        sender_balance.balance -= amount
        receiver_balance.balance += amount


        transaction = Transaction(
            user_id=current_user.id,
            type="transfer",
            amount=amount,
            currency=currency,
            target_user_id=target_user.id,
            currency_symbol=get_currency_symbol(currency),
            currency_from=currency
        )

        db.session.add(transaction)
        db.session.commit()

        return{
            "message": "Transfer successful",
            "balance": round(sender_balance.balance, 2),
            "currency": currency,
            "target_user_id": target_user.id,
            "target_username": target_user.username ,
            "amount": round(amount, 2)
        },200
    

    @staticmethod
    def transaction(user):

        if not user:
            return jsonify({"error": "User not found"}), 404

        transactions = (
            Transaction.query
            .filter(
                (Transaction.user_id == user.id) | (Transaction.target_user_id == user.id)
            )
            .order_by(Transaction.created_at.asc())  
            .all()
        )
    
        user_balances = {} 
        transactions_response = []

    
        for t in transactions:
            
            currency = t.currency

            if currency not in user_balances:
                user_balances[currency] = 0.0

            status = "unknown"  

            if t.type == "top_up":
            
                user_balances[currency] += t.amount
                status = "credited"
            
            elif t.type == "exchange" and t.converted_amount:
            
                user_balances[t.currency_from] = user_balances.get(t.currency_from, 0) - t.amount
                user_balances[t.currency_to] = user_balances.get(t.currency_to, 0) + t.converted_amount
                status = "debited" if t.currency_from == currency else "credited"

            elif t.type == "transfer":
                if t.target_user_id == user.id:  # This means the user is the recipient
                    user_balances[t.currency] += t.amount
                    status = "credited"
                else:  # This means the user is the sender
                    user_balances[t.currency] -= t.amount
                    status = "debited"

            if t.type == "transfer":
                if t.target_user_id == user.id:
                    direction_field = {
                        "received_from": t.user.username if t.user else None,
                        "target_user_id": None,
                        "target_username": None
                    }
                else:
                    direction_field = {
                        "to": f"{t.amount:.2f}{t.currency_symbol}",
                        "target_user_id": t.target_user_id,
                        "target_username": t.target_user.username if t.target_user else None
                    }
            else:
                direction_field = {
                    "to": "-",
                    "target_user_id": None,
                    "target_username": None
                }        

            transactions_response.append({
                "id": t.id,
                "type": t.type,
                "amount": round(t.amount, 2),
                "currency_from": t.currency_from or None,
                "currency_to": t.currency_to or None,
                "converted_amount": round(t.converted_amount, 2) if t.converted_amount else None,
                "target_user_id": t.target_user_id,
                "currency_symbol": t.currency_symbol,
                "currency": t.currency,
                "balance": round(user_balances[t.currency], 2),
                "timestamp": t.created_at.isoformat(),
                "to": f"{t.amount:.2f}{t.currency_symbol}" if t.type == "transfer" else "-",
                "target_username": t.target_user.username if t.target_user_id else None,
                "status": status ,
                **direction_field,
            })

        transactions_response.reverse()

        return{
            "transactions": transactions_response
        },200
