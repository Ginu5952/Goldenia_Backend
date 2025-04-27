# 🌟 Goldenia 

Flask-based REST API for the Goldenia Wallet app. Supports user registration, login, wallet operations like top-up, transfers, currency exchange, and admin-level access to all users and transactions.

## 🚀 Tech Stack

- Python 3
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- PostgreSQL
- Flasgger (Swagger UI for API docs)
- Flask-Migrate
- CORS
- dotenv

## 📦 Setup Instructions

### 1. Clone the Repository
#### Open your terminal and run following commands 
```bash
git clone https://github.com/Ginu5952/Goldenia_Backend.git
cd Goldenia_Backend
code .
```

### 2. Create Virtual Environment and Install Dependencies
Run following commands in Terminal
```
python -m venv venv
source venv/bin/activate     # on Windows: venv\Scripts\activate
pip install -r requirements.txt
````

# PostgreSQL Setup Guide

## 1. Install PostgreSQL

To install PostgreSQL, follow the instructions for your operating system:

- **[PostgreSQL Downloads](https://www.postgresql.org/download/)**  
  (Choose your OS: macOS, Windows, or Linux)

For macOS, you can use Homebrew:
```bash
brew install postgresql
```
Check the installed version:
```
psql --version
```
Log in to PostgreSQL:
```
psql -U yourusername -d postgres
```

Create a new database:
```
CREATE DATABASE goldenia_wallet;
\q
```

Connect to your new database:
```
psql -U yourusername -d goldenia_wallet
```


### Create .env File
In your root directory create a .env file
```
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_db
SQLALCHEMY_TRACK_MODIFICATIONS=False
````

### Set Up Database

```
flask db init
flask db migrate
flask db upgrade
```

# Note:- To set the first user as an admin
```
psql -U yourusername -d goldenia_wallet
UPDATE "user"
SET is_admin = 't'  
WHERE id = 1;
```

### Run the Server
```
flask run
# or
python app.py
```
Server will run at: http://127.0.0.1:5000/

# 📑 Swagger Docs

Available at:
http://127.0.0.1:5000/apidocs/

* Use Bearer token from login response to test protected endpoints



