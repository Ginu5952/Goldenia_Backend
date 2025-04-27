from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS 
from flasgger import Swagger
from dotenv import load_dotenv
import os

from models.user import db
from auth import auth_bp  
from controllers.user_controller import user_bp
from controllers.exchange_controller import exchange_bp
from controllers.transaction_controller import transaction_bp
from admin import admin_bp

# Load environment variables from .env file
load_dotenv()

def create_app(config_name="development"):
    app = Flask(__name__)


    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_VERIFY_SUB'] = False

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'supersecretkey'

    db.init_app(app)              
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app)


    swagger = Swagger(app, template_file='swagger.yml')


    app.register_blueprint(auth_bp)  
    app.register_blueprint(user_bp)
    app.register_blueprint(exchange_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def home():
        return "🎉 Goldenia Wallet API Running!"
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)