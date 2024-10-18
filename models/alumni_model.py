from extensions import db
from datetime import datetime

class Alumni(db.Model):
    __tablename__ = 'alumni'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    college_name = db.Column(db.String(100), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    company = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    skills = db.Column(db.String(200), nullable=True)
    availability = db.Column(db.JSON, nullable=True)
    about = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    progress_bar = db.Column(db.Float, nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    github = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    password = db.Column(db.String(128), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
