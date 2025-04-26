from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction, UserBalance
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
def get_all_transactions():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or not user.is_admin:
        return jsonify({"message": "Access forbidden: Admins only"}), 403

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


