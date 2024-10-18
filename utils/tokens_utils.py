import jwt
import os

SECRET_KEY = 'your_jwt_secret'

def generate_access_token(user_id, username, email):
    return jwt.encode({
        'user_id': user_id,
        'username': username,
        'email': email,
        'exp': os.getenv("ACCESSTOKEN_EXPIRY") 
    }, os.getenv("ACCESSTOKEN_SECRET_KEY"), algorithm='HS256')

def generate_refresh_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': os.getenv("REFRESHTOKEN_EXPIRY") 
    }, os.getenv("REFRESHTOKEN_SECRET_KEY"), algorithm='HS256')
