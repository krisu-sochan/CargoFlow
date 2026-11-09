from datetime import datetime,timezone
from db import db
class Company(db.Model):
    __tablename__='companies'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150), nullable=False)
    email=db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    users = db.relationship('User', back_populates='company')
class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(255), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    role=db.Column(db.String(20), nullable=False)
    company_id=db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    company = db.relationship('Company', back_populates='users')