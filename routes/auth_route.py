from flask import Blueprint, request
from services.auth_service import register_user,verify_otp,login_user,reset_password,change_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return register_user(data)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return login_user(data)

@auth_bp.route('/verify-otp', methods=['POST'])
def verify():
    data = request.get_json()
    return verify_otp(data)

@auth_bp.route('/reset-password', methods=['POST'])
def reset():
    data = request.get_json()
    return reset_password(data)

@auth_bp.route('/change-password', methods=['POST'])
def change():
    data = request.get_json()
    return change_password(data)