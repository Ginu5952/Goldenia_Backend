from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.exchange_service import ExchangeService

exchange_bp = Blueprint('exchange', __name__, url_prefix='/user')

@exchange_bp.route('/exchange', methods=['POST'])
@jwt_required()
def exchange_currency():
   
    identity = get_jwt_identity()
    user = User.query.get(identity)
    data = request.get_json()
    amount = data.get('amount')
    currency_from = data.get('currency_from')
    currency_to = data.get('currency_to')

    result = ExchangeService.exchange(user, amount, currency_from, currency_to)
    return jsonify(
            result
        ), 200