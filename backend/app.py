import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import URL
from db import db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.exc import IntegrityError
from models import Company, User

from flask import Flask, request,session



load_dotenv(Path(__file__).resolve().parent / '.env')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application. Please set FLASK_SECRET_KEY in .env file.")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
    drivername="postgresql+pg8000",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT","5432"),
    database=os.getenv("DB_NAME")
)
db.init_app(app)
@app.route('/api/health', methods=['GET'])
def health():
    db.session.execute(text('SELECT 1'))
    return {'status': 'ok',
            'message': 'Service is running',
              'database': 'connected'}, 200
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {'status': 'error', 'message': 'Invalid JSON data'}, 400
    required_fields = [
    'company_name',
    'first_name',
    'last_name',
    'email',
    'password'
    ]

    for field in required_fields:
        value = data.get(field)

        if not isinstance(value, str) or not value.strip():
            return {'status': 'error',
            'message': f'Missing or invalid field: {field}' }, 400

    company_name = data["company_name"].strip()
    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    if len(password) < 8:
        return {'status': 'error', 'message': 'Password must be at least 8 characters long'}, 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return {'status': 'error', 'message': 'Invalid email format'}, 400
    if (len(company_name)>150 or len(first_name)>100 or len(last_name)>100 or len(email)>255):
        return {'status': 'error', 'message': 'Input exceeds maximum length'}, 400
    try:
        company = Company(name = company_name, email=email)
        db.session.add(company)
        db.session.flush()  
        user = User(
first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role='admin',
                    company_id=company.id
        )
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'status': 'error', 'message': 'Email already exists'}, 409
    return {'status': 'success', 'message': 'User registered successfully'}, 201
@app.route('/api/auth/login',methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data,dict):
        return{'status':'error','message':'Invalid JSON data'},400
    email = data.get('email')
    password = data.get('password')
    if not isinstance(email,str) or not isinstance(password,str):
        return {'status':'error','message':'Missing email or password'},400
    email=email.strip().lower()
    if not email or not password:
        return {'status':'error','message':'Missing email or password'},400
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if user is None or not check_password_hash(user.password_hash,password):
        return {'status':'error','message':'Invalid email or password'},401
    session.clear()
    session['user_id']=user.id
    return {
        'message':'Login successful',
        'user':{
            'id':user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'role':user.role,
            'company_id':user.company_id
        }
    },200
@app.route('/api/auth/me',methods=['GET'])
def get_current_user():
    user_id=session.get('user_id')
    if  user_id is None:
        return{'error':'Not signed in'},401
    user=db.session.get(User,user_id)
    if user is None:
        session.clear()
        return{'error':'User not found'},404
    return {
        
        'id':user.id,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'email':user.email,
        'role':user.role,
        'company_id':user.company_id
    }
@app.route('/api/auth/logout',methods=['POST'])
def logout():
    session.clear()
    return {'message':'Logout successful'},200