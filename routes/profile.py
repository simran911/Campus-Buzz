from flask import request, jsonify, current_app, Blueprint
from functools import wraps
import jwt
from models.student_model import Student
from models.alumni_model import Alumni
from extensions import db
import os
from dotenv import load_dotenv

profile_bp = Blueprint('profile', __name__)

import logging

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        print("this is my token",token)
        logging.info(f'Received token: {token}')  # Log the token for debugging
        if not token:
            return jsonify({'error': 'Authentication required!'}), 401
        try:
            # Decode the token using the JWT secret key from the Flask app config
            secret_key = os.getenv('ACCESSTOKEN_SECRET_KEY')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    # Fetch the user based on user_id from either the Student or Alumni table
    user = Student.query.get(user_id) or Alumni.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found!'}), 404

    if request.method == 'GET':
        # Return the current user profile details
        profile_data = {
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'avatar': user.avatar,
            'college_name': user.college_name,
            'graduation_year': getattr(user, 'graduation_year', None),  # Alumni specific
            'company': getattr(user, 'company', None),  # Alumni specific
            'job_title': getattr(user, 'job_title', None),  # Alumni specific
            'course': getattr(user, 'course', None),  # Student specific
            'year_of_study': getattr(user, 'year_of_study', None),  # Student specific
            'interests': user.interests,
            'linkedin': user.linkedin,
            'github': user.github,
            'description': user.description
        }
        return jsonify(profile_data), 200

    elif request.method == 'POST':
        # Update user profile details
        data = request.get_json()

        user.full_name = data.get('full_name', user.full_name)
        user.avatar = data.get('avatar', user.avatar)
        user.college_name = data.get('college_name', user.college_name)
        user.interests = data.get('interests', user.interests)
        user.linkedin = data.get('linkedin', user.linkedin)
        user.github = data.get('github', user.github)
        user.description = data.get('description', user.description)

        # Specific fields for Alumni and Student
        if isinstance(user, Alumni):
            user.graduation_year = data.get('graduation_year', user.graduation_year)
            user.company = data.get('company', user.company)
            user.job_title = data.get('job_title', user.job_title)
        elif isinstance(user, Student):
            user.course = data.get('course', user.course)
            user.year_of_study = data.get('year_of_study', user.year_of_study)

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully!'}), 200
