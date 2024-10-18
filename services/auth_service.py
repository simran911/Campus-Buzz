import random
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from extensions import db, mail
from models.student_model import Student
from models.alumni_model import Alumni
from flask_mail import Message
from utils.response_handler import ResponseHandler
from utils.tokens_utils import generate_access_token,generate_refresh_token
from flask import make_response

temp_users = {}  # Temporary store for holding unverified users

#* FOR SENDING OTP
def send_otp_email(email, otp):
    msg = Message(
        "Your OTP Code",
        sender=mail.default_sender,
        recipients=[email]
    )
    msg.body = f"Your OTP code is: {otp}. Please use it to verify your account."
    mail.send(msg)

#* FOR REGISTER USER
def register_user(data):
    user_type = data.get('user_type')

    if user_type not in ['student', 'alumni']:
        return ResponseHandler.error('Invalid user type. Must be "student" or "alumni".', 400)

    if 'username' not in data or 'email' not in data or 'password' not in data:
        return ResponseHandler.error('Missing required fields', 400)

     # Check if user already exists in the main database
    if user_type == 'student' and Student.query.filter_by(email=data['email']).first():
        return ResponseHandler.error('Student with this email already exists!', 400)
    elif user_type == 'alumni' and Alumni.query.filter_by(email=data['email']).first():
        return ResponseHandler.error('Alumni with this email already exists!', 400)

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

    return ResponseHandler.success(message=f'{user_type.capitalize()} Please verify your email with the OTP sent to you.', status_code=201)


##* FOR VIRIFY OTP:
def verify_otp(data):
    email = data.get('email')
    otp = data.get('otp')

    # Check if the user is in the temporary store and if OTP matches
    temp_user = temp_users.get(email)
    if not temp_user or temp_user['otp'] != otp:
        return ResponseHandler.error('Invalid OTP or email!', 400)

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

    # Remove user from the temporary store after successful verification
    db.session.add(new_user)
    db.session.commit()

    temp_users.pop(email)

    return ResponseHandler.success(message=f'{temp_user["user_type"].capitalize()} OTP verified successfully! Registration complete!', status_code=200)

#* FOR LOGIN :
def login_user(data):
    email = data.get('email')
    password = data.get('password')

    user = Student.query.filter_by(email=email).first() or Alumni.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Create access and refresh tokens
        # access_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, 'your_jwt_secret', algorithm='HS256')
        # refresh_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)}, 'your_jwt_secret', algorithm='HS256')

        access_token = generate_access_token(user.id, user.username, user.email)
        refresh_token = generate_refresh_token(user.id)

        user.refresh_token = refresh_token
        db.session.commit()

        # Set cookies
        options = {
        'httponly': True,
        'secure': os.getenv("FLASK_ENV") == "production",  # true in production
        'samesite': 'None' if os.getenv("FLASK_ENV") == "production" else 'Lax',
        }

        response = make_response()  # Create an empty response object
        response.set_cookie(
            'access_token', 
            access_token,  
            httponly=options['httponly'], 
            secure=options['secure'], 
            samesite=options['samesite']) 
        response.set_cookie(
            'refresh_token',
            httponly=options['httponly'], 
            secure=options['secure'], 
            samesite=options['samesite'])

        return ResponseHandler.success(data={'access_token': access_token, 'refresh_token': refresh_token}, message='Login successful', status_code=200)

    return ResponseHandler.error('Invalid email or password!', 401)


#* FOR RESET PASSWORD:
def reset_password(data):
    email = data.get('email')
    
    user = Student.query.filter_by(email=email).first() or Alumni.query.filter_by(email=email).first()

    if not user:
        return ResponseHandler.error('Email not found!', 404)

    user.otp = str(random.randint(100000, 999999))  # Generate OTP
    send_otp_email(email, user.otp)
    db.session.commit()
    
    return ResponseHandler.success(message='Password reset OTP has been sent to your email!', status_code=200)

##* FOR CHANGE PASSWORD:
def change_password(data):
    email = data.get('email')
    new_password = data.get('new_password')
    otp = data.get('otp')

    user = Student.query.filter_by(email=email, otp=otp).first() or Alumni.query.filter_by(email=email, otp=otp).first()

    if not user:
        return ResponseHandler.error('Invalid OTP or email!', 400)

    user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.otp = None  # Clear OTP after changing password
    db.session.commit()

    return ResponseHandler.success(message='Password changed successfully!', status_code=200)