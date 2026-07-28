# Forbes Marshall Employee Management System

A full-stack application for employee management with admin and employee roles.

## Features
✅ **Authentication System** - Login with role-based access (Admin/Employee)
✅ **Admin Dashboard** - Add and manage employees
✅ **Employee Homepage** - Shows employee name and can access pallet data system
✅ **Database Integration** - MySQL database for storing user credentials and employee data
✅ **JWT Token Authentication** - Secure token-based authentication

## Tech Stack
- **Frontend:** React 19.1.0, React Router, Axios
- **Backend:** Flask, Flask-JWT-Extended, Flask-SQLAlchemy
- **Database:** MySQL (5.7, 8.0 or later)

## Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- pip (Python package manager)
- **MySQL Database** (see Database Setup below)

### Database Setup (MySQL) - REQUIRED FIRST

You must set up MySQL Database before running the application:

#### Option 1: MySQL Community Server (Free for Development)
1. Download: https://dev.mysql.com/downloads/mysql/
2. Install MySQL and create a database instance
3. Create database and user:
```sql
CREATE DATABASE forbes_app;
CREATE USER 'forbes_app'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON forbes_app.* TO 'forbes_app'@'localhost';
FLUSH PRIVILEGES;
```

#### Option 2: MySQL via Docker
```bash
docker run --name mysql-app -e MYSQL_ROOT_PASSWORD=your_password -e MYSQL_DATABASE=forbes_app -p 3306:3306 -d mysql:latest
```

#### Option 3: Cloud MySQL Services
1. Use AWS RDS for MySQL, Azure Database for MySQL, or Google Cloud SQL
2. Get connection details from your cloud provider console

### Environment Configuration
Create `.env` file in `backend/` directory:
```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=forbes_app
JWT_SECRET_KEY=your-secure-secret-key-here
```

### Step 1: Frontend Setup

```bash
# Navigate to project root (where package.json is)
npm install

# Start the React development server
npm start
```

The frontend will open at `http://localhost:3000`

### Step 2: Backend Setup

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend will start at `http://localhost:5000`

## Default Credentials

### Admin Account
```
Email: admin@gmail.com
Password: root
```

### Demo Employee (add via admin panel)
You can add employee accounts through the admin dashboard after logging in as admin.

## Usage

### 1. **Login Page**
- Navigate to `http://localhost:3000`
- Enter credentials (admin@gmail.com/root for admin access)

### 2. **Admin Dashboard** (if logged in as admin)
- **Add New Employee**: Fill in name, email, and password
- **View All Employees**: See list of all employees
- **Delete Employee**: Remove employee from system

### 3. **Employee Homepage** (if logged in as employee)
- Shows: "Welcome, [Employee Name]!"
- Can use the pallet data calculation system
- Download logs CSV
- Logout button in top right

## API Endpoints

All endpoints (except /api/login) require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

### Authentication
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user
- `GET /api/user` - Get current user info

### Employee Management
- `GET /api/employees` - Get all employees (admin only)
- `POST /api/add-employee` - Add employee (admin only)
- `DELETE /api/delete-employee/<id>` - Delete employee (admin only)

### Legacy Endpoints
- `POST /submit` - Original pallet data submission
- `GET /download` - Download logs

## Project Structure

```
react-frontend-main/
├── src/
│   ├── App.js                 # Main app with routing
│   ├── App.css
│   ├── Login.js               # Login component
│   ├── Login.css
│   ├── Home.js                # Employee homepage
│   ├── Home.css
│   ├── Admin.js               # Admin dashboard
│   ├── Admin.css
│   └── ...
├── public/
├── package.json
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── requirements.txt        # Python dependencies
│   └── README.md
└── README.md
```

## Database Schema

### Users Table
```
id (Integer, Primary Key)
email (String, Unique)
password (String, hashed)
role (String) - 'admin' or 'employee'
name (String) - Employee name
```

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running and accessible at the host and port configured in `.env`
- Verify `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME` are correct
- Check MySQL user permissions for creating and modifying tables

### Environment Variables Not Loading
- Ensure `.env` file exists in `backend/` directory
- Check that `python-dotenv` is installed
- Verify variable names match exactly (case-sensitive)

### Frontend not connecting to backend
- Ensure backend is running on `http://localhost:5000`
- Check CORS is enabled in Flask
- Clear browser cache and local storage if needed

### Port conflicts
- **Frontend port 3000:** `npm start -- --port 3001`
- **Backend port 5000:** Edit `app.py` and change port number

### JWT Token expired
- Login again to get a new token
- Token expires after 30 days by default

### Database issues
- Delete `backend/employees.db` to reset database
- Admin account will be recreated on next backend start

## Security Notes
⚠️ This is a demo application. For production:
1. Change `JWT_SECRET_KEY` in `backend/app.py`
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Add rate limiting
5. Add input validation and sanitization
6. Use a production-grade database

## Development

### Adding a new employee in admin panel
1. Login as admin (email: admin, password: root)
2. Fill in the form on the left side
3. Click "Add Employee"
4. Employee will appear in the list on the right

### Modifying employee data
Currently, the system only supports adding and deleting employees. To modify, delete and re-add with new data.

## Support
For issues or questions, check the API responses in the browser console for error messages.

