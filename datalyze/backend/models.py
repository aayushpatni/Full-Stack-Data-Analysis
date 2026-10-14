from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    streak = db.Column(db.Integer, default=0)
    last_upload = db.Column(db.String(50), nullable=True)
    joined = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    otp = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    expires = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(20), default='register') # 'register' or 'login'
