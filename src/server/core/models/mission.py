from core import db
from datetime import datetime

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    id_local = db.Column(db.Integer)
    id_server = db.Column(db.Integer)

    status = db.Column(db.String(20), nullable=False)
    info =  db.Column(db.String(100))
    agv = db.Column(db.String(5))

    step_id = db.Column(db.Integer)  # id do passo, comecando de zero.
    step_type = db.Column(db.String(20))  #StepTypeEnum
    position_target = db.Column(db.Integer) # CurrentTargetId - assumimos sempre apenas 1.

    dt_created = db.Column(db.DateTime, default=datetime.utcnow)
    dt_updated = db.Column(db.DateTime, default=datetime.utcnow)
