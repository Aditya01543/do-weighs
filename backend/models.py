from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'employee'
    name = db.Column(db.String(120), nullable=True)  # Only for employees
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'name': self.name
        }

class ItemMaster(db.Model):
    __tablename__ = 'item_master'

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    unit_weight = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'item_code': self.item_code,
            'description': self.description,
            'unit_weight': self.unit_weight,
        }

class ReportRecord(db.Model):
    __tablename__ = 'report_records'

    id = db.Column(db.Integer, primary_key=True)
    scanned_by = db.Column(db.String(120), nullable=True)
    item_code = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    master_unit_weight = db.Column(db.Float, nullable=True)
    manual_unit_weight = db.Column(db.Float, nullable=True)
    gross_weight = db.Column(db.Float, nullable=False)
    pallet_weight = db.Column(db.Float, nullable=True)
    net_weight = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    rounded_quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'scanned_by': self.scanned_by,
            'item_code': self.item_code,
            'description': self.description,
            'master_unit_weight': self.master_unit_weight,
            'manual_unit_weight': self.manual_unit_weight,
            'gross_weight': self.gross_weight,
            'pallet_weight': self.pallet_weight,
            'net_weight': self.net_weight,
            'quantity': self.quantity,
            'rounded_quantity': self.rounded_quantity,
            'created_at': self.created_at.isoformat(),
        }
