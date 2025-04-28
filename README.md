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

## Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/get-started) (for running containers)
- [Docker Compose](https://docs.docker.com/compose/install/) (to manage multi-container apps)


## 📦 Setup Instructions

### 1. Clone the Repository
#### Open your terminal and run following commands 
```bash
git clone https://github.com/Ginu5952/Goldenia_Backend.git
cd Goldenia_Backend
code .
```

## Update the .env file:


SECRET_KEY: This is a Flask security key for sessions and other cryptographic operations. You should generate a secure key.

To generate a secure SECRET_KEY, run the following command in your terminal:

```
python3 -c 'import secrets; print(secrets.token_hex(24))'

```

Copy the generated string and paste it into the .env file 

```
SECRET_KEY=your-secure-secret-key

```
SECRET_KEY

DATABASE_URL: Docker will automatically create and configure the PostgreSQL database for you.

Update the DATABASE_URL in the .env file. Replace the placeholders with your own values:
```
DATABASE_URL=postgresql://your-user-name:your-password@db:5432/your-db-name

```
`your-database-username`: Username for your PostgreSQL database (e.g., goldenia_user).

`your-database-password`: Password for your PostgreSQL user (e.g., goldenia).

`your-database-name`: The name of your database (e.g., goldenia_wallet).

`Note: The db part in the DATABASE_URL refers to the Docker service name for PostgreSQL in your docker-compose.yml file. Docker will automatically handle the internal networking.`

### Start the application with Docker Compose
Run the following command to build and start the Docker containers:

```
docker-compose up --build
````
This command will build Docker images for the frontend, backend, and database, and start all services inside Docker containers.

## Access the Application

Once the containers are running, you can access the application:

Backend (API): http://127.0.0.1:5000


# 📑 Swagger Docs

Available at:
http://127.0.0.1:5000/apidocs/

* Use Bearer token from login response to test protected endpoints



