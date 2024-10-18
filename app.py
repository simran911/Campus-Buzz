import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from extensions import db, mail
from routes.auth import auth_bp
from routes.profile import profile_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')  # Use your desired database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER') 
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') 
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER') 
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'  # Convert to boolean
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'  # Convert to boolean
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
mail.init_app(app)

# Register the auth blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

# Home route to check if the server is running
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Flask server is running!"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all tables
    app.run(debug=True)
