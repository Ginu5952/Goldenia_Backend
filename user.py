from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction

user_bp = Blueprint('user', __name__, url_prefix='/user')

# TOP UP
#-----------------#

@user_bp.route('/top-up', methods=['POST'])
@jwt_required()
def top_up():
    data = request.get_json()
    amount = data.get('amount')

    if not amount or amount <= 0:
        return jsonify({'message': 'Invalid top-up amount'}), 400

    identity = get_jwt_identity()
    #user = User.query.get(identity['id'])
    user = User.query.get(int(identity))

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.balance += amount

    transaction = Transaction(
        user_id=user.id,
        type='top_up',
        amount=amount
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'message': 'Top-up successful',
        'balance': user.balance
    }), 200

# SEND TRANSFER
#-----------------#

@user_bp.route('/transfer', methods=['POST'])
@jwt_required() 
def transfer():
    
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

    if not current_user:
        return jsonify({"message": "Current user not found"}), 404

    if not target_user:
        return jsonify({"message": "Target user not found"}), 404

    if current_user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

   
    current_user.balance -= amount

   
    target_user.balance += amount

   
    transaction = Transaction(
        user_id=current_user.id,
        type="transfer",
        amount=amount
    )

   
    db.session.add(transaction)
    db.session.commit()

    
    return jsonify({
        "message": "Transfer successful",
        "balance": current_user.balance
    }), 200


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "balance": user.balance
    })

# Transaction History
#-----------------#

@user_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    identity = get_jwt_identity()
   # user = User.query.get(identity if isinstance(identity, int) else identity["id"])
    user = User.query.get(int(identity))
    if not user:
        return jsonify({"error": "User not found"}), 404

    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc()).all()
    
    return jsonify({
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "amount": t.amount,
                "currency": t.currency,
                "timestamp": t.created_at.isoformat(),
                "target_user_id": t.target_user_id
            }
            for t in transactions
        ]
    }), 200


# Fetch User's Data 
#-----------------#

@user_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user_by_id(id):
   
    user = User.query.get(id)

    if not user:
        return jsonify({"error": "User not found"}), 404

   
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,  
        "balance": user.balance,
        "created_at": user.created_at.isoformat()
    }), 200



@user_bp.route('/exchange', methods=['POST'])
@jwt_required()
def exchange_currency():
   
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

    exchange_rate = 0.85  

    if currency_from == "USD" and currency_to == "EUR":
        converted_amount = amount * exchange_rate
    elif currency_from == "EUR" and currency_to == "USD":
        converted_amount = amount / exchange_rate
    else:
        return jsonify({"message": "Currency pair not supported"}), 400

    if currency_from == "USD" and user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    if currency_from == "EUR" and user.balance < amount * exchange_rate:
        return jsonify({"message": "Insufficient balance"}), 400

    if currency_from == "USD":
        user.balance -= amount
    elif currency_from == "EUR":
        user.balance -= amount * exchange_rate

   
    if currency_to == "USD":
        user.balance += converted_amount
    elif currency_to == "EUR":
        user.balance += converted_amount * exchange_rate


    transaction = Transaction(
        user_id=user.id,
        type="exchange",
        amount=amount,
        currency_from=currency_from,
        currency_to=currency_to,
        converted_amount=converted_amount
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Exchange successful",
        "balance": user.balance
    }), 200
