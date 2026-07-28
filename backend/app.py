from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
try:
    from backend.models import db, User, ItemMaster, ReportRecord
except ImportError:
    from models import db, User, ItemMaster, ReportRecord
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote
import pandas as pd
import io

# Load environment variables
load_dotenv()
from math import floor

BASE_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = BASE_DIR / 'build'


def get_database_uri():
    database_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
    if database_url:
        return database_url

    db_host = os.getenv('DB_HOST', '').strip().lower()
    db_user = os.getenv('DB_USER', '').strip()
    db_password = os.getenv('DB_PASSWORD', '').strip()
    db_name = os.getenv('DB_NAME', '').strip()

    if db_host and db_host not in {'localhost', '127.0.0.1', '::1'} and db_user and db_name:
        db_port = os.getenv('DB_PORT', '3306')
        encoded_password = quote(db_password, safe='')
        return f'mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'

    sqlite_path = BASE_DIR / 'instance' / 'forbes_app.sqlite'
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return f'sqlite:///{sqlite_path}'


app = Flask(__name__, static_folder=str(BUILD_DIR), static_url_path='')
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

MASTER_ITEMS = {}
FALLBACK_UNIT_WEIGHT = 5  # per user request


def load_master_data():
    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        xlsx_path = os.path.normpath(os.path.join(base, 'Doweighs.xlsx'))
        if not os.path.exists(xlsx_path):
            print(f"MASTER: Doweighs.xlsx not found at {xlsx_path}")
            return

        df = pd.read_excel(xlsx_path, engine='openpyxl')
        cols_lower = [str(c).strip().lower() for c in df.columns]
        item_col = None
        description_col = None
        weight_col = None

        for idx, col in enumerate(cols_lower):
            normalized = col.replace(' ', '')
            if normalized in ('itemcode', 'item_code', 'itemcode') and item_col is None:
                item_col = df.columns[idx]
            if normalized in ('description', 'itemdescription') and description_col is None:
                description_col = df.columns[idx]
            if normalized in ('unitweight', 'unit_weight', 'unitweight', 'weight', 'unitweight') and weight_col is None:
                weight_col = df.columns[idx]

        if item_col is None:
            item_col = df.columns[0]
        if description_col is None and len(df.columns) > 1:
            description_col = df.columns[1]
        if weight_col is None and len(df.columns) > 2:
            weight_col = df.columns[2]

        for _, row in df.iterrows():
            item_code = str(row[item_col]).strip()
            if not item_code or item_code.lower() in ('nan', 'none'):
                continue
            description = str(row[description_col]).strip() if description_col is not None else ''
            try:
                unit_weight = float(row[weight_col]) if weight_col is not None and pd.notna(row[weight_col]) else None
            except Exception:
                unit_weight = None
            MASTER_ITEMS[item_code] = {
                'item_code': item_code,
                'description': description,
                'unit_weight': unit_weight,
            }

        print(f"MASTER: Loaded {len(MASTER_ITEMS)} items from {xlsx_path}")
    except Exception as e:
        print(f"MASTER: Failed to load Doweighs.xlsx: {e}")

load_master_data()

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        # Create default admin if not exists, or update existing admin email
        old_admin = User.query.filter_by(email='admin').first()
        if old_admin:
            old_admin.email = 'admin@gmail.com'
            db.session.commit()
        else:
            new_admin = User.query.filter_by(email='admin@gmail.com').first()
            if not new_admin:
                new_admin = User(email='admin@gmail.com', role='admin')
                new_admin.set_password('root')
                db.session.add(new_admin)
                db.session.commit()
    except Exception as e:
        print(f"DATABASE: Unable to initialize database tables: {e}")

# Routes

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


@app.route('/api/login', methods=['POST'])
def login():
    """Login route - accepts email and password"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user info"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@app.route('/api/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees - admin only"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    employees = User.query.filter_by(role='employee').all()
    return jsonify([emp.to_dict() for emp in employees]), 200

@app.route('/api/add-employee', methods=['POST'])
@jwt_required()
def add_employee():
    """Add new employee - admin only"""
    try:
        print(f"DEBUG: Request Content-Type: {request.content_type}")
        print(f"DEBUG: Request Data: {request.get_data()}")
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        print(f"DEBUG: Parsed JSON: {data}")
        
        email = data.get('email')
        name = data.get('name')
        password = data.get('password', 'defaultpass')
        
        print(f"DEBUG: Adding employee - Name: {name}, Email: {email}")
        
        if not email or not name:
            return jsonify({'error': 'Email and name required'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"DEBUG: Email already exists: {email}")
            return jsonify({'error': 'Email already exists'}), 400
        
        new_employee = User(email=email, name=name, role='employee')
        new_employee.set_password(password)
        db.session.add(new_employee)
        db.session.commit()
        
        print(f"DEBUG: Employee added successfully - ID: {new_employee.id}")
        
        return jsonify({
            'message': 'Employee added successfully',
            'employee': new_employee.to_dict()
        }), 201
    except Exception as e:
        print(f"DEBUG: Error adding employee: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/delete-employee/<int:emp_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(emp_id):
    """Delete employee - admin only"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    employee = User.query.get(emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({'message': 'Employee deleted successfully'}), 200

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout - frontend should clear token"""
    return jsonify({'message': 'Logged out successfully'}), 200

def get_item_master(item_code):
    item_code = str(item_code or '').strip()
    if not item_code:
        return None
    override = ItemMaster.query.filter_by(item_code=item_code).first()
    if override:
        return {
            'item_code': override.item_code,
            'description': override.description,
            'unit_weight': override.unit_weight,
        }
    return MASTER_ITEMS.get(item_code)

@app.route('/api/items', methods=['GET'])
def get_items():
    query = request.args.get('q', '').strip().lower()
    results = []
    seen = set()

    if query:
        for item_code, item in MASTER_ITEMS.items():
            if query in item_code.lower() or query in str(item.get('description', '')).lower():
                results.append(item)
                seen.add(item_code)
            if len(results) >= 50:
                break
    else:
        for item_code, item in list(MASTER_ITEMS.items())[:50]:
            results.append(item)
            seen.add(item_code)

    if query:
        overrides = ItemMaster.query.filter(ItemMaster.item_code.ilike(f'%{query}%')).all()
        for override in overrides:
            if override.item_code not in seen:
                results.append(override.to_dict())
                if len(results) >= 50:
                    break

    return jsonify(results), 200

@app.route('/api/item/<item_code>', methods=['GET'])
def get_item(item_code):
    item = get_item_master(item_code)
    if not item:
        return jsonify({'item_code': item_code, 'description': '', 'unit_weight': None}), 200
    return jsonify(item), 200

@app.route('/api/submit', methods=['POST'])
def submit():
    """Submit a calculation request for form1 or form2."""
    data = request.get_json() or {}
    item_code = str(data.get('item_code') or data.get('itemCode') or '').strip()
    item = get_item_master(item_code)
    master_weight = item.get('unit_weight') if item else None
    description = item.get('description') if item else ''

    total_weight = data.get('total_weight')
    pallet_weight = data.get('pallet_weight')
    unit_weight = data.get('unit_weight')
    override_unit_weight = data.get('override_unit_weight')
    quantity = data.get('quantity')

    try:
        total_weight = float(total_weight)
    except Exception:
        return jsonify({'error': 'Gross Weight must be a number'}), 400
    try:
        pallet_weight = float(pallet_weight) if pallet_weight not in (None, '', '0') else 0.0
    except Exception:
        return jsonify({'error': 'Pallet Weight must be a number'}), 400

    net_weight = total_weight - pallet_weight
    if net_weight < 0:
        return jsonify({'error': 'Net weight cannot be negative'}), 400

    if quantity is not None and quantity != '':
        try:
            quantity = float(quantity)
        except Exception:
            return jsonify({'error': 'Quantity must be a number'}), 400
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than zero'}), 400
        unit_weight_calc = net_weight / quantity
        return jsonify({
            'item_code': item_code,
            'description': description,
            'net_weight': round(net_weight, 4),
            'quantity': round(quantity, 4),
            'unit_weight_used': round(unit_weight_calc, 4),
            'master_unit_weight': master_weight,
            'rounded_quantity': round(quantity),
        }), 200

    if override_unit_weight not in (None, '', 0):
        try:
            unit_weight = float(override_unit_weight)
        except Exception:
            return jsonify({'error': 'Override unit weight must be numeric'}), 400
    elif unit_weight is None or unit_weight == '':
        unit_weight = master_weight if master_weight is not None else FALLBACK_UNIT_WEIGHT

    try:
        unit_weight = float(unit_weight)
    except Exception:
        return jsonify({'error': 'Unit weight must be numeric'}), 400

    if unit_weight <= 0:
        unit_weight = FALLBACK_UNIT_WEIGHT

    quantity = net_weight / unit_weight if unit_weight else 0
    return jsonify({
        'item_code': item_code,
        'description': description,
        'net_weight': round(net_weight, 4),
        'quantity': round(quantity, 4),
        'rounded_quantity': round(quantity),
        'unit_weight_used': round(unit_weight, 4),
        'master_unit_weight': master_weight,
    }), 200

@app.route('/api/save-record', methods=['POST'])
@jwt_required(optional=True)
def save_record():
    data = request.get_json() or {}
    user = None
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
    except Exception:
        user = None

    item_code = str(data.get('item_code') or '').strip()
    description = data.get('description') or ''
    master_unit_weight = data.get('master_unit_weight')
    manual_unit_weight = data.get('manual_unit_weight')
    gross_weight = data.get('gross_weight')
    pallet_weight = data.get('pallet_weight')
    net_weight = data.get('net_weight')
    quantity = data.get('quantity')
    rounded_quantity = data.get('rounded_quantity')
    save_master = data.get('save_master', False)

    try:
        gross_weight = float(gross_weight)
        pallet_weight = float(pallet_weight) if pallet_weight not in (None, '', '0') else 0.0
        net_weight = float(net_weight)
        quantity = float(quantity)
        rounded_quantity = int(round(float(rounded_quantity)))
        if master_unit_weight not in (None, ''):
            master_unit_weight = float(master_unit_weight)
        if manual_unit_weight not in (None, ''):
            manual_unit_weight = float(manual_unit_weight)
    except Exception:
        return jsonify({'error': 'Numeric data required for save'}), 400

    record = ReportRecord(
        scanned_by=user.email if user else None,
        item_code=item_code,
        description=description,
        master_unit_weight=master_unit_weight,
        manual_unit_weight=manual_unit_weight,
        gross_weight=gross_weight,
        pallet_weight=pallet_weight,
        net_weight=net_weight,
        quantity=quantity,
        rounded_quantity=rounded_quantity,
        created_at=datetime.utcnow(),
    )
    db.session.add(record)

    if save_master and item_code:
        override = ItemMaster.query.filter_by(item_code=item_code).first()
        if not override:
            override = ItemMaster(item_code=item_code, description=description, unit_weight=manual_unit_weight or master_unit_weight)
            db.session.add(override)
        else:
            override.description = description or override.description
            override.unit_weight = manual_unit_weight or master_unit_weight

    db.session.commit()
    return jsonify({'message': 'Record saved successfully', 'record': record.to_dict()}), 201

@app.route('/api/history', methods=['GET'])
def get_history():
    records = ReportRecord.query.order_by(ReportRecord.created_at.desc()).limit(200).all()
    return jsonify([rec.to_dict() for rec in records]), 200

@app.route('/download', methods=['GET'])
def download():
    records = ReportRecord.query.order_by(ReportRecord.created_at.desc()).all()
    output = io.StringIO()
    output.write('id,scanned_by,item_code,description,master_unit_weight,manual_unit_weight,gross_weight,pallet_weight,net_weight,quantity,rounded_quantity,created_at\n')
    for rec in records:
        output.write('"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"\n'.format(
            rec.id,
            rec.scanned_by or "",
            rec.item_code,
            (rec.description or "").replace('"', '""'),
            rec.master_unit_weight or "",
            rec.manual_unit_weight or "",
            rec.gross_weight,
            rec.pallet_weight or "",
            rec.net_weight,
            rec.quantity,
            rec.rounded_quantity,
            rec.created_at.isoformat()
        ))
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='report_records.csv')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith('api/') or path.startswith('download'):
        return jsonify({'error': 'Not found'}), 404

    build_path = BUILD_DIR / path
    if path and build_path.exists():
        return send_from_directory(str(BUILD_DIR), path)
    return send_from_directory(str(BUILD_DIR), 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
