from core import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    roles = db.Column(db.String(10), nullable=False)
    token = db.Column(db.String(32), unique=True)
    token_date = db.Column(db.DateTime, default=datetime.now)