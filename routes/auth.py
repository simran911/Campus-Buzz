from flask import Blueprint, request, jsonify
from models.student_model import Student
from models.alumni_model import Alumni
from extensions import db, mail
from flask_mail import Message
import random
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import bcrypt
import jwt
import uuid
import json
import random
import requests 

auth_bp = Blueprint('auth', __name__)


def send_otp_email(email, otp):
    msg = Message(
        "Your OTP Code",
        sender=mail.default_sender,
        recipients=[email]
    )
    msg.body = f"Your OTP code is: {otp}. Please use it to verify your account."
    mail.send(msg)

# Temporary store for holding unverified users (in-memory dictionary as an example)
temp_users = {}

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    user_type = data.get('user_type')

    if user_type not in ['student', 'alumni']:
        return jsonify({'error': 'Invalid user type. Must be "student" or "alumni".'}), 400

    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists in the main database
    if user_type == 'student':
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Student with this email already exists!'}), 400
    elif user_type == 'alumni':
        if Alumni.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Alumni with this email already exists!'}), 400

    # Generate OTP and hash password
    otp = str(random.randint(100000, 999999))
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Save user temporarily (in memory or Redis)
    temp_users[data['email']] = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'otp': otp,
        'user_type': user_type
    }

    # Send OTP email
    send_otp_email(data['email'], otp)

    return jsonify({'message': f'{user_type.capitalize()} Please verify your email with the OTP sent to you.'}), 201

# OTP Verification Route
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    # Check if the user is in the temporary store and if OTP matches
    temp_user = temp_users.get(email)
    if not temp_user or temp_user['otp'] != otp:
        return jsonify({'error': 'Invalid OTP or email!'}), 400

    # Create user in the main database based on user type
    if temp_user['user_type'] == 'student':
        new_user = Student(
            username=temp_user['username'],
            email=temp_user['email'],
            password=temp_user['password'],
            is_verified=True
        )
    elif temp_user['user_type'] == 'alumni':
        new_user = Alumni(
            username=temp_user['username'],
            email=temp_user['email'],
            password=temp_user['password'],
            is_verified=True
        )

    db.session.add(new_user)
    db.session.commit()

    # Remove user from the temporary store after successful verification
    temp_users.pop(email)

    return jsonify({'message': f'{temp_user["user_type"].capitalize()} email verified successfully! Registration complete!'}), 200

# Login Route
@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Student.query.filter_by(email=email).first() or Alumni.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Create access and refresh tokens
        access_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, 'your_jwt_secret', algorithm='HS256')
        refresh_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)}, 'your_jwt_secret', algorithm='HS256')

        # Save tokens in the database (if you have fields for them)
        user.refresh_token = refresh_token
        db.session.commit()

        # Create a response object
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        
        # Set cookies
        response.set_cookie('access_token', access_token, httponly=True, secure=False)  # Set secure=True if using HTTPS
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=False)  # Set secure=True if using HTTPS

        return response
    return jsonify({'error': 'Invalid email or password!'}), 401

# Password Reset Route
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    
    user = Student.query.filter_by(email=email).first() or Alumni.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Email not found!'}), 404

    # Send password reset link or OTP here
    user.otp = str(random.randint(100000, 999999))  # Generate OTP
    send_otp_email(email, user.otp)
    db.session.commit()
    
    return jsonify({'message': 'Password reset OTP has been sent to your email!'}), 200

# Change Password Route
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')
    otp = data.get('otp')

    user = Student.query.filter_by(email=email, otp=otp).first() or Alumni.query.filter_by(email=email, otp=otp).first()

    if not user:
        return jsonify({'error': 'Invalid OTP or email!'}), 400

    user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.otp = None  # Clear OTP after changing password
    db.session.commit()

    return jsonify({'message': 'Password changed successfully!'}), 200
