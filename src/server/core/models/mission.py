from core import db
from datetime import datetime

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
