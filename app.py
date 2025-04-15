from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS 
from dotenv import load_dotenv
import os

from models import db
from auth import auth_bp  
from user import user_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_VERIFY_SUB'] = False

db.init_app(app)              
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

app.register_blueprint(auth_bp)  
app.register_blueprint(user_bp)

@app.route('/')
def home():
    return "🎉 Goldenia Wallet API Running!"

if __name__ == '__main__':
    app.run(debug=True)
