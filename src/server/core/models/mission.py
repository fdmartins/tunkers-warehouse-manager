from core import db
from datetime import datetime

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    id_local = db.Column(db.Integer)
    id_server = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False)
    current_step_type = db.Column(db.String(20), nullable=False)

    dt_created = db.Column(db.DateTime, default=datetime.utcnow)
    dt_updated = db.Column(db.DateTime, default=datetime.utcnow)
