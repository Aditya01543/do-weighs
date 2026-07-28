import os
from dotenv import load_dotenv
from sqlalchemy import inspect
from app import app, db, User

load_dotenv()

print("=" * 50)
print("DATABASE CONFIGURATION CHECK")
print("=" * 50)

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_mysql_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'forbes_app')

print(f"DB User: {DB_USER}")
print(f"DB Host: {DB_HOST}:{DB_PORT}")
print(f"DB Name: {DB_NAME}")
print()

try:
    with app.app_context():
        # Check if tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("✓ Database connection successful!")
        print(f"Tables found: {tables}")
        print()
        
        # Check users table
        if 'users' in tables:
            users = User.query.all()
            print(f"✓ Users table exists with {len(users)} users:")
            for user in users:
                print(f"  - {user.email} ({user.role})")
        else:
            print("✗ Users table not found!")
            
except Exception as e:
    print(f"✗ Database connection failed!")
    print(f"Error: {str(e)}")
    print()
    print("Make sure:")
    print("1. MySQL server is running")
    print("2. Database 'forbes_app' exists")
    print("3. Credentials in .env are correct")
