# Backend Setup Guide

This is a Flask backend for the Forbes Marshall Employee Management System using MySQL Database.

## Installation

### 1. Prerequisites - MySQL Database Setup

**You need to set up MySQL Database externally:**

#### Option A: MySQL Community Server (Recommended for Development)
- Download and install MySQL Community Server from: https://dev.mysql.com/downloads/mysql/
- Create a database for the application
- Create a user with appropriate permissions

#### Option B: MySQL via Docker (Easy Setup)
```bash
docker run --name mysql-app -e MYSQL_ROOT_PASSWORD=your_password -e MYSQL_DATABASE=forbes_app -p 3306:3306 -d mysql:latest
```

#### Option C: Cloud MySQL Services
- Use AWS RDS for MySQL
- Use Azure Database for MySQL
- Use Google Cloud SQL for MySQL
- Use any other cloud-hosted MySQL service

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL database details:
```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=forbes_app
JWT_SECRET_KEY=your-secure-secret-key
```

### 4. Create Database Tables

Run the Flask app once to create tables:
```bash
python app.py
```

The application will automatically create the required tables on first run.

## Default Admin Credentials
- **Email:** admin@gmail.com
- **Password:** root

## API Endpoints

### Authentication
- **POST /api/login** - Login with email and password
- **POST /api/logout** - Logout (requires JWT token)

### Employee Management (Admin only)
- **GET /api/employees** - Get all employees
- **POST /api/add-employee** - Add new employee
- **DELETE /api/delete-employee/<id>** - Delete employee

### User Info
- **GET /api/user** - Get current user info (requires JWT token)

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running and accessible at the host and port configured in `.env`
- Verify `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME` are correct
- Check MySQL user permissions for creating and modifying tables

### Environment Variables Not Loading
- Ensure `.env` file exists in the backend directory
- Check that `python-dotenv` is installed
- Verify variable names match exactly

## Security Notes
- Change the `JWT_SECRET_KEY` to a strong, random key in production
- Use strong passwords for database users

If port 5000 is already in use, modify the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port here
```

Also update the API calls in the React components to use the new port.

### CORS errors
Make sure both frontend and backend are running:
- Frontend: `npm start` on port 3000
- Backend: `python app.py` on port 5000
