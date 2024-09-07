from core import db
from datetime import datetime

class Button:
    def __init__(self):
        pass

    ip = "?"
    last_life = datetime.now()

class ButtonCall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_device = db.Column(db.String(20), primary_key=True)      # IP de onde foi feita a requisicao.
    telegram_type = db.Column(db.String(20), nullable=False)    # ACTION / LIFE
    material_type = db.Column(db.String(20), nullable=False)    # BOBINA / PALLET
    action_type = db.Column(db.String(20), nullable=False)      # ABASTECE / RETIRA
    situation = db.Column(db.String(20), nullable=False)        # COMPLETO / INCOMPLETO
    machine = db.Column(db.Integer, nullable=False)             # ID MAQUINA
    product = db.Column(db.String(50), nullable=False)          # SKU
    bitola = db.Column(db.Float, nullable=False)                # Bitola 
    dt_creation = db.Column(db.DateTime, default=datetime.now())
