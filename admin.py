from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.transaction import Transaction


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ----------------- ADMIN ROUTES ----------------- #

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or not user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    users = User.query.all()
    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "balances": [
                    {
                        "currency": balance.currency,
                        "balance": round(balance.balance, 2)
                    } for balance in u.balances
                ],
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ]
    }), 200

@admin_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_all_transactions_by_id():
   
    identity = get_jwt_identity()
    admin_user = User.query.get(identity)
    
    if not admin_user or not admin_user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=20, type=int)

    query = Transaction.query

    if user_id:
        query = query.filter(
            (Transaction.user_id == user_id) | (Transaction.target_user_id == user_id)
        )

    pagination = query.order_by(Transaction.created_at.asc()).paginate(page=page, per_page=page_size, error_out=False)
    transactions = pagination.items

    transactions_response = []

    usd_balance = 0 
    eur_balance = 0
    

   
    for t in transactions:  
        sender = User.query.get(t.user_id)
        receiver = User.query.get(t.target_user_id) if t.target_user_id else None

      
        if t.type == "transfer":
            if user_id:  
                if t.user_id == user_id:
                    status = "debited"
                elif t.target_user_id == user_id:
                    status = "credited"
                else:
                    status = "debited"  
            else:
                status = "debited"  
        else:
            status = "credited" if t.type == "top_up" else "debited"

        transaction_obj = {
            "id": t.id,
            "type": t.type,
            "amount": round(t.amount, 2),
            "currency": t.currency,
            "currency_symbol": t.currency_symbol,
            "timestamp": t.created_at.isoformat(),
            "status": status,
        }

       
        if t.type == "transfer":
            if status == "debited":
                if receiver:
                    transaction_obj["target_user"] = {
                        "target_user_id": receiver.id,
                        "target_username": receiver.username
                    }
                    transaction_obj["to"] = f"{t.amount:.2f}{t.currency_symbol}"
                else:
                    transaction_obj["to"] = "-"
            elif status == "credited":
                if sender:
                    transaction_obj["received_from"] = sender.username
                    transaction_obj["received_from_id"] = sender.id
                    transaction_obj["to"] = f"{t.amount:.2f}{t.currency_symbol}"
                else:
                    transaction_obj["to"] = "-"

        elif t.type == "top_up":
            transaction_obj["to"] = "-"

        elif t.type == "exchange":
            transaction_obj["to"] = "-"
            transaction_obj["currency_from"] = t.currency_from
            transaction_obj["currency_to"] = t.currency_to
            transaction_obj["converted_amount"] = round(t.converted_amount, 2) if t.converted_amount else None

        # Update balance
        if t.type == "exchange":
            if t.currency_from == "USD" and t.currency_to == "EUR":
                usd_balance -= t.amount
                eur_balance += t.converted_amount
            elif t.currency_from == "EUR" and t.currency_to == "USD":
                eur_balance -= t.amount
                usd_balance += t.converted_amount
        else:
            if t.currency == "USD":
                if status == "credited":
                    usd_balance += t.amount
                elif status == "debited":
                    usd_balance -= t.amount
            elif t.currency == "EUR":
                if status == "credited":
                    eur_balance += t.amount
                elif status == "debited":
                    eur_balance -= t.amount

        # Set correct balance according to transaction currency
        if t.type == "exchange":
            if t.currency_to == "USD":
                transaction_obj["balance"] = round(usd_balance, 2)
            elif t.currency_to == "EUR":
                transaction_obj["balance"] = round(eur_balance, 2)
        else:
            if t.currency == "USD":
                transaction_obj["balance"] = round(usd_balance, 2)
            elif t.currency == "EUR":
                transaction_obj["balance"] = round(eur_balance, 2)

        transactions_response.append(transaction_obj)

    # Reverse back because you reversed to calculate balance
    transactions_response = list(reversed(transactions_response))

    return jsonify({
        "transactions": transactions_response,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "user_id": user_id,
        "username": User.query.get(user_id).username if user_id else None
    }), 200



@admin_bp.route('/user/<int:id>', methods=['GET'])
@jwt_required()
def get_user_by_id_admin(id):
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
        "balances": [
            {
                "currency": balance.currency,
                "balance": round(balance.balance, 2)
            } for balance in user.balances
        ],
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    }), 200


