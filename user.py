from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction, UserBalance
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')


def get_currency_symbol(currency: str):
    if currency == "USD":
        return "$"
    elif currency == "EUR":
        return "€"
    return ""

# ----------------- USER ROUTES ----------------- #

@user_bp.route("/users", methods=["GET"])
def get_all_users():
 
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        })

    return jsonify({"users": users_list}), 200

@user_bp.route("/top-up", methods=["POST"])
@jwt_required()
def top_up():
    """
    Top up the user's balance.
    
    ---
    tags:
      - User
    parameters:
      - in: body
        name: body
        description: The amount to top-up for the user
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              description: Amount to top up
              example: 50
    responses:
      200:
        description: Balance updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                balance:
                  type: number
                  description: Updated balance after top-up
                  example: 150.00
                currency_symbol:
                  type: string
                  description: Currency symbol
                  example: "$"
                message:
                  type: string
                  description: Response message
                  example: "Top-up successful"
      400:
        description: Invalid amount
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    user = User.query.get(int(identity))

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    amount = data.get("amount")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    
    currency = user.currency  
    
    user_balance = UserBalance.query.filter_by(user_id=user.id, currency=currency).first()

    if not user_balance:
       
        user_balance = UserBalance(user_id=user.id, currency=currency, balance=0.0)
        db.session.add(user_balance)
    
   
    user_balance.balance += amount

    transaction = Transaction(
        user_id=user.id,
        type="top_up",
        amount=amount,
        currency=currency,
        currency_symbol="$",
        created_at=datetime.utcnow()
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "balance": round(user_balance.balance, 2), 
        "currency_symbol": "$",
        "message": "Top-up successful"
    }), 200


    current_user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    target_user_id = data.get('target_user_id')

    if not amount or not target_user_id:
        return jsonify({"message": "Amount and target_user_id are required"}), 400
    if amount <= 0:
        return jsonify({"message": "Amount must be greater than 0"}), 400

    current_user = User.query.get(current_user_id)
    target_user = User.query.get(target_user_id)

    if not current_user or not target_user:
        return jsonify({"message": "User not found"}), 404

    if current_user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

    current_user.balance -= amount
    target_user.balance += amount

    transaction = Transaction(
        user_id=current_user.id,
        type="transfer",
        amount=amount,
        currency=current_user.currency,
        target_user_id=target_user_id,
        currency_symbol=get_currency_symbol(current_user.currency)
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Transfer successful",
        "balance": round(current_user.balance, 2)
    }), 200

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile with balances.
    
    ---
    tags:
      - User
    responses:
      200:
        description: Successfully retrieved user profile and balances
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: User ID
                  example: 1
                username:
                  type: string
                  description: Username of the user
                  example: "johndoe"
                balances:
                  type: array
                  description: List of the user's balances for different currencies
                  items:
                    type: object
                    properties:
                      currency:
                        type: string
                        description: Currency type (e.g., USD, EUR)
                        example: "USD"
                      amount:
                        type: number
                        description: Amount in the respective currency
                        example: 150.00
                      symbol:
                        type: string
                        description: Currency symbol
                        example: "$"
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

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

    return jsonify({
        "id": user.id,
        "username": user.username,
        "balances": balances
    }), 200


@user_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
  
    """
    Get the history of transactions for the authenticated user.
    
    ---
    tags:
      - User
    responses:
      200:
        description: Successfully retrieved the user's transactions
        content:
          application/json:
            schema:
              type: object
              properties:
                transactions:
                  type: array
                  description: A list of transaction objects
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: The transaction ID
                        example: 1
                      type:
                        type: string
                        description: The type of transaction (e.g., top_up, exchange, transfer)
                        example: "top_up"
                      amount:
                        type: number
                        description: The amount involved in the transaction
                        example: 50.00
                      currency_from:
                        type: string
                        description: The currency from which funds are being moved (for exchange and transfer types)
                        example: "USD"
                      currency_to:
                        type: string
                        description: The currency to which funds are being moved (for exchange and transfer types)
                        example: "EUR"
                      converted_amount:
                        type: number
                        description: The converted amount for exchange transactions
                        example: 45.00
                      target_user_id:
                        type: integer
                        description: The ID of the target user (for transfers)
                        example: 3
                      currency_symbol:
                        type: string
                        description: The symbol of the currency (e.g., $, €, etc.)
                        example: "$"
                      currency:
                        type: string
                        description: The currency used in the transaction
                        example: "USD"
                      balance:
                        type: number
                        description: The balance after the transaction is applied
                        example: 150.00
                      timestamp:
                        type: string
                        description: The timestamp when the transaction was created
                        example: "2025-04-25T12:00:00"
                      to:
                        type: string
                        description: The recipient of the transfer (if applicable)
                        example: "50.00$"
                      target_username:
                        type: string
                        description: The username of the target user (for transfers)
                        example: "roy"
      404:
        description: User not found
    """
    
    identity = get_jwt_identity()
    user = User.query.get(int(identity))

    if not user:
        return jsonify({"error": "User not found"}), 404

    transactions = (
        Transaction.query
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.asc())  
        .all()
    )
   
    user_balances = {} 
    transactions_response = []

   
    for t in transactions:
        
        currency = t.currency

        if currency not in user_balances:
          user_balances[currency] = 0.0

        if t.type == "top_up":
           
          user_balances[currency] += t.amount
           
        elif t.type == "exchange" and t.converted_amount:
           
            user_balances[t.currency_from] = user_balances.get(t.currency_from, 0) - t.amount
            user_balances[t.currency_to] = user_balances.get(t.currency_to, 0) + t.converted_amount

        elif t.type == "transfer":
            user_balances[t.currency_from] = user_balances.get(t.currency_from, 0) - t.amount
           
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
            "target_username": t.target_user.username if t.target_user_id else None
        })

    transactions_response.reverse()

    return jsonify({
        "transactions": transactions_response
    }), 200


@user_bp.route('/exchange', methods=['POST'])
@jwt_required()
def exchange_currency():
    """
    Exchange currencies for the authenticated user.
    
    ---
    tags:
      - User
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 50
            currency_from:
              type: string
              example: "USD"
            currency_to:
              type: string
              example: "EUR"
    responses:
      200:
        description: Exchange was successful and balances were updated
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                converted_amount:
                  type: number
                balance_from:
                  type: number
                balance_to:
                  type: number
                currency_from:
                  type: string
                currency_to:
                  type: string
                currency_symbol:
                  type: string
      400:
        description: Invalid amount or currency pair
      404:
        description: User not found
    
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    amount = data.get('amount')
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')

    if not amount or amount <= 0:
        return jsonify({"message": "Amount must be greater than zero"}), 400
    if currency_from == currency_to:
        return jsonify({"message": "Currencies must be different"}), 400

    exchange_rates = {
        ("USD", "EUR"): 0.88,
        ("EUR", "USD"): 1.14,
    }

    rate = exchange_rates.get((currency_from, currency_to))
    if not rate:
        return jsonify({"message": "Currency pair not supported"}), 400

    balance_from = next((b for b in user.balances if b.currency == currency_from), None)
    balance_to = next((b for b in user.balances if b.currency == currency_to), None)

    if not balance_from or balance_from.balance < amount:
        return jsonify({"message": f"Insufficient balance in {currency_from}"}), 400

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
        currency=currency_to,
        currency_symbol=get_currency_symbol(currency_to)
    )

    db.session.add(transaction)
    db.session.commit()

    user.balance = sum([b.balance for b in user.balances])

    return jsonify({
        "message": "Exchange successful",
        "converted_amount": round(converted_amount, 2),
        "balance_from": round(balance_from.balance, 2),
        "balance_to": round(balance_to.balance, 2),
        "currency_from": currency_from,
        "currency_to": currency_to,
        "currency_symbol": get_currency_symbol(currency_to)
    }), 200

@user_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """
    Transfer amount from the authenticated user to another user.

    ---
    tags:
      - User
    parameters:
      - in: body
        name: transfer
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              description: The amount to transfer
              example: 50.0
            target_user_id:
              type: integer
              description: The ID of the target user
              example: 2
            currency:
              type: string
              description: The currency for the transfer
              example: "USD"
    responses:
      200:
        description: Transfer was successful and balances were updated
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                balance:
                  type: number
                currency:
                  type: string
                target_user_id:
                  type: integer
                target_username:
                  type: string
                amount:
                  type: number
      400:
        description: Invalid or missing parameters, or insufficient balance
      404:
        description: User not found
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    target_user_id = data.get('target_user_id')
    currency = data.get('currency') 

    if not all([amount, target_user_id, currency]):
        return jsonify({"message": "Amount, target_user_id, and currency are required"}), 400
    if amount <= 0:
        return jsonify({"message": "Amount must be greater than 0"}), 400

    current_user = User.query.get(current_user_id)
    target_user = User.query.get(target_user_id)

    if not current_user or not target_user:
        return jsonify({"message": "User not found"}), 404

   
    sender_balance = UserBalance.query.filter_by(user_id=current_user.id, currency=currency).first()
    receiver_balance = UserBalance.query.filter_by(user_id=target_user.id, currency=currency).first()

    if not sender_balance or sender_balance.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

   
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

    return jsonify({
        "message": "Transfer successful",
        "balance": round(sender_balance.balance, 2),
        "currency": currency,
        "target_user_id": target_user.id,
        "target_username": target_user.username ,
        "amount": round(amount, 2)
    }), 200


