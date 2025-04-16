from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction

user_bp = Blueprint('user', __name__, url_prefix='/user')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# TOP UP
#-----------------#

@user_bp.route('/top-up', methods=['POST'])
@jwt_required()
def top_up():

    """
    Top-up Balance
    ---
    tags:
      - User
    summary: Add funds to user's wallet
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - name: amount
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 1000
    responses:
      200:
        description: Top-up successful
        schema:
          type: object
          properties:
            message:
              type: string
            balance:
              type: number
      400:
        description: Invalid top-up amount
      404:
        description: User not found
    """
   
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

    """
    Transfer Money
    ---
    tags:
      - User Operations
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - target_user_id
          properties:
            amount:
              type: number
              format: float
              example: 10
            target_user_id:
              type: integer
              example: 1
    responses:
      200:
        description: Transfer successful
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Transfer successful
                balance:
                  type: number
                  format: float
                  example: 990
      400:
        description: Invalid or insufficient data
      404:
        description: User not found
      401:
        description: Unauthorized request (JWT required)
    """
    
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

    """
    Get Transaction History
    ---
    tags:
      - User Operations
    security:
      - Bearer: []
    responses:
      200:
        description: A list of transactions for the logged-in user
        content:
          application/json:
            schema:
              type: object
              properties:
                transactions:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      type:
                        type: string
                        example: "top_up"
                      amount:
                        type: number
                        format: float
                        example: 1000
                      currency:
                        type: string
                        example: "USD"
                      timestamp:
                        type: string
                        format: date-time
                        example: "2025-04-16T12:30:00Z"
                      target_user_id:
                        type: integer
                        example: 2
      404:
        description: User not found
      401:
        description: Unauthorized request (JWT required)
    """

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

    """
    Exchange Currency
    ---
    tags:
      - User Operations
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - currency_from
            - currency_to
          properties:
            amount:
              type: number
              example: 100
            currency_from:
              type: string
              example: "USD"
            currency_to:
              type: string
              example: "EUR"
    responses:
      200:
        description: Currency exchange successful
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Exchange successful"
                balance:
                  type: number
                  example: 85.0
      400:
        description: Invalid amount, insufficient balance, or unsupported currency pair
      404:
        description: User not found
      401:
        description: Unauthorized request (JWT required)
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



# Admin-only route to fetch all users
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():

    """
    Get All Users (Admin Only)
    ---
    tags:
      - Admin Operations
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully retrieved the list of users
        content:
          application/json:
            schema:
              type: object
              properties:
                users:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      username:
                        type: string
                      email:
                        type: string
                      balance:
                        type: number
                      is_admin:
                        type: boolean
                      created_at:
                        type: string
                        format: date-time
                      updated_at:
                        type: string
                        format: date-time
      403:
        description: Access forbidden, only admins can view the users
      401:
        description: Unauthorized request (JWT required)
    """

    identity = get_jwt_identity()
    user = User.query.get(identity)

    # Check if the user is an admin
    if not user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    # Fetch all users
    users = User.query.all()
    
    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "balance": u.balance,
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ]
    }), 200


# Admin-only route to fetch all transactions
@admin_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_all_transactions():

    """
    Get All Transactions (Admin Only)
    ---
    tags:
      - Admin Operations
    summary: Retrieve all user transactions (Admin access required)
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully retrieved all transactions
        content:
          application/json:
            schema:
              type: object
              properties:
                transactions:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      user_id:
                        type: integer
                      type:
                        type: string
                      amount:
                        type: number
                      currency:
                        type: string
                      timestamp:
                        type: string
                        format: date-time
                      target_user_id:
                        type: integer
                        nullable: true
      403:
        description: Access forbidden - Admins only
      401:
        description: Unauthorized - Missing or invalid JWT
    """
     
    identity = get_jwt_identity()
    user = User.query.get(identity)

   
    if not user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    # Fetch all transactions
    transactions = Transaction.query.all()

    return jsonify({
        "transactions": [
            {
                "id": t.id,
                "user_id": t.user_id,
                "type": t.type,
                "amount": t.amount,
                "currency": t.currency,
                "timestamp": t.created_at.isoformat(),
                "target_user_id": t.target_user_id
            }
            for t in transactions
        ]
    }), 200


@admin_bp.route('/user/<int:id>', methods=['GET'])
@jwt_required()
def get_user_by_id_admin(id):
    """
    Get User by ID (Admin Only)
    ---
    tags:
      - Admin Operations
    summary: Retrieve user details by user ID (Admin access required)
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to fetch
    responses:
      200:
        description: User details retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
                balance:
                  type: number
                is_admin:
                  type: boolean
                created_at:
                  type: string
                  format: date-time
      401:
        description: Unauthorized - Missing or invalid token
      403:
        description: Forbidden - Admin access required
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    admin_user = User.query.get(identity)

    if not admin_user or not admin_user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    user = User.query.get(id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "balance": user.balance,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    }), 200
