from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from models.user import User

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    
    identity = get_jwt_identity()
    user = User.query.get(identity)
    result = UserService.get_user_profile(user)

    return jsonify(result), 200
