from core import db
from datetime import datetime

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    status = db.Column(db.String(20), nullable=False)
    dt_created = db.Column(db.DateTime, default=datetime.utcnow)
    dt_update = db.Column(db.DateTime, default=datetime.utcnow)
