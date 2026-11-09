from app import app
from db import db
from models import Company,User


with app.app_context():
    db.create_all()

    print("Tabele zostały utworzone!")