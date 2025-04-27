from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.transaction_service import TransactionService

transaction_bp = Blueprint('transaction', __name__, url_prefix='/user')


@transaction_bp.route("/top-up", methods=["POST"])
@jwt_required()
def top_up():
   
    identity = get_jwt_identity()
    data = request.get_json()
    amount = data.get("amount")
 
    result = TransactionService.top_up(identity, amount)
    
    return jsonify(
        result
    ), 200


@transaction_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
   
    current_user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    target_user_id = data.get('target_user_id')
    currency = data.get('currency') 

    result = TransactionService.transfer(current_user_id,target_user_id, amount,currency)

    if isinstance(result, tuple):
        response_data, status_code = result
        return jsonify(response_data), status_code
    else:
        return jsonify(result), 200



@transaction_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():

    identity = get_jwt_identity()
    user = User.query.get(int(identity))

    result = TransactionService.transaction(user)
    return jsonify(
        result
    ), 200

   

