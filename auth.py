from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():

    """
    User Signup
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: jinu
            email:
              type: string
              example: jinu@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: User created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: User created successfully
      400:
        description: Missing required fields
      409:
        description: User already exists
    """

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'User already exists'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
   
    """
    User Login
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: jinu@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Successful login
        schema:
          type: object
          properties:
            access_token:
              type: string
            role:
              type: string
      401:
        description: Invalid email or password
    """
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Use only user.id as identity (must be a string, int, or UUID)
    access_token = create_access_token(identity=str(user.id))

    role = 'admin' if user.is_admin else 'user'

    return jsonify({
        'access_token': access_token,
        'role': role
        }), 200
