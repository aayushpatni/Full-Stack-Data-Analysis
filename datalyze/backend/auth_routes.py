# Authentication Routes
from flask import Blueprint, request, jsonify, session
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, OTP
from utils import generate_otp, send_otp_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    password = data.get('password', '')

    if not email or not name or not password:
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered. Please Sign In.'}), 409

    otp = generate_otp()
    
    # Remove any existing pending registration OTPs for this email
    OTP.query.filter_by(email=email, purpose='register').delete()
    
    hashed_password = generate_password_hash(password)
    new_otp = OTP(email=email, otp=otp, name=name, password=hashed_password, expires=time.time() + 600, purpose='register')
    db.session.add(new_otp)
    db.session.commit()

    sent, msg = send_otp_email(email, otp, purpose="Registration")
    print(f"[OTP] {email} -> {otp} (Email sent: {sent})")

    if sent:
        return jsonify({'success': True, 'message': f'OTP sent to {email}!', 'email_sent': True})
    else:
        return jsonify({
            'success': True, 
            'message': f'OTP sent! (Demo OTP: {otp})', 
            'demo_otp': otp, 
            'email_sent': False
        })

@auth_bp.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()

    record = OTP.query.filter_by(email=email, purpose='register').first()
    if not record:
        return jsonify({'success': False, 'message': 'No OTP found. Register first.'}), 400
    if time.time() > record.expires:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': False, 'message': 'OTP expired'}), 400
    if record.otp != otp:
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400

    new_user = User(email=email, name=record.name, password=record.password, streak=0, joined=datetime.now().isoformat())
    db.session.add(new_user)
    db.session.delete(record)
    db.session.commit()
    
    session['user'] = email
    return jsonify({'success': True, 'message': 'Account created!',
                    'user': {'name': new_user.name, 'email': email, 'streak': 0}})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    otp = generate_otp()
    OTP.query.filter_by(email=email, purpose='login').delete()
    
    login_otp = OTP(email=email, otp=otp, expires=time.time() + 300, purpose='login')
    db.session.add(login_otp)
    db.session.commit()
    
    sent, msg = send_otp_email(email, otp, purpose="Login")
    print(f"[LOGIN OTP] {email} -> {otp} (Email sent: {sent})")

    if sent:
        return jsonify({'success': True, 'message': f'OTP sent to {email}!', 'email_sent': True, 'step': 'otp'})
    else:
        return jsonify({
            'success': True, 
            'message': f'OTP sent! (Demo OTP: {otp})', 
            'demo_otp': otp, 
            'email_sent': False, 
            'step': 'otp'
        })

@auth_bp.route('/api/login-verify', methods=['POST'])
def login_verify():
    data = request.json
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()

    record = OTP.query.filter_by(email=email, purpose='login').first()
    if not record or time.time() > record.expires or record.otp != otp:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 400

    db.session.delete(record)
    db.session.commit()
    
    session['user'] = email
    user = User.query.filter_by(email=email).first()
    return jsonify({'success': True, 'user': {'name': user.name, 'email': email, 'streak': user.streak}})

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@auth_bp.route('/api/me')
def me():
    email = session.get('user')
    if not email:
        return jsonify({'authenticated': False}), 401
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'authenticated': False}), 401
        
    return jsonify({'authenticated': True, 'user': {'name': user.name, 'email': email, 'streak': user.streak}})
