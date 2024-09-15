from core import db
from datetime import datetime

class Button:
    def __init__(self):
        # CARREGA ARQUIVO .INI COM WHITELIST E OUTRAS INFORMACOES CUSTOMIZAVEIS...
        # TODO.
        pass

    ip = "?"
    last_life = datetime.now()


class ButtonStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_device = db.Column(db.String(20), unique=True, nullable=False)
    last_call = db.Column(db.DateTime, default=datetime.now())
    last_life = db.Column(db.DateTime, default=datetime.now())
    life_sequence = db.Column(db.Integer, nullable=False)  
    life_previous_sequence = db.Column(db.Integer, nullable=False)  
    status_message = db.Column(db.String(50))

class ButtonCall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_device = db.Column(db.String(20), primary_key=False)      # IP de onde foi feita a requisicao.
    message_type = db.Column(db.String(20), nullable=False)    # ACTION / LIFE
    material_type = db.Column(db.String(20), nullable=False)    # BOBINA / PALLET
    action_type = db.Column(db.String(20), nullable=False)      # ABASTECE / RETIRA
    situation = db.Column(db.String(20), nullable=False)        # COMPLETO / INCOMPLETO
    id_machine = db.Column(db.Integer, nullable=False)             # ID MAQUINA
    gauge = db.Column(db.String(10), nullable=False)                # Bitola 
    product = db.Column(db.String(50), nullable=False)          # SKU

    mission_status = db.Column(db.String(50), nullable=False) 

    id_navithor = db.Column(db.Integer) # id de uma missao cadastrada no navithor.

    dt_creation = db.Column(db.DateTime, default=datetime.now())


    def __str__(self):
        # Formata todos os atributos da instância como uma string
        return (f"ButtonCall("
                f"id={self.id}, "
                f"ip_device={self.ip_device}, "
                f"message_type={self.message_type}, "
                f"material_type={self.material_type}, "
                f"action_type={self.action_type}, "
                f"situation={self.situation}, "
                f"id_machine={self.id_machine}, "
                f"bitola={self.gauge}, "
                f"product={self.product}, "
                f"mission_status={self.mission_status}, "
                f"dt_creation={self.dt_creation})")