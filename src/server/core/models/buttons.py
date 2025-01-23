from core import db
from datetime import datetime

class Button:
    def __init__(self):
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
    id_button =  db.Column(db.String(20), primary_key=False)     # identificacao da botoeira, string, pode ser um texto se desejado.
    message_type = db.Column(db.String(20), nullable=False)    # ACTION / LIFE
    material_type = db.Column(db.String(20), nullable=False)    # BOBINA / PALLET
    action_type = db.Column(db.String(20), nullable=False)      # ABASTECE / RETIRA
    situation = db.Column(db.String(20), nullable=False)        # COMPLETO / INCOMPLETO
    id_machine = db.Column(db.Integer, nullable=False)             # ID MAQUINA

    sku = db.Column(db.String(30))                   # sku
    gauge = db.Column(db.String(10))                # Bitola 
    product = db.Column(db.String(50))          # product name

    reserved_pos = db.Column(db.String(150), default="")  # armazena posicoes que deveram ser reservadas para este movimento.

    mission_status = db.Column(db.String(50), nullable=False) 
    info = db.Column(db.String(500)) 

    id_navithor = db.Column(db.Integer) # id de uma missao cadastrada no navithor.

    dt_creation = db.Column(db.DateTime, default=datetime.now())

    def set_reserved_pos(self, lista):
        # Converte a lista para uma string separada por vírgulas
        self.reserved_pos = ','.join(map(str, lista))

    def get_reserved_pos(self):
        # Converte a string de volta para uma lista de inteiros
        if self.reserved_pos:
            return [int(item) for item in self.reserved_pos.split(',')]
        return []
    

    def __str__(self):
        # Formata todos os atributos da instância como uma string
        return (f"ButtonCall("
                f"id={self.id}, "
                f"ip_device={self.ip_device}, "
                f"id_button={self.id_button}, "
                f"message_type={self.message_type}, "
                f"material_type={self.material_type}, "
                f"action_type={self.action_type}, "
                f"situation={self.situation}, "
                f"id_machine={self.id_machine}, "
                f"bitola={self.gauge}, "
                f"product={self.product}, "
                f"sku={self.sku}, "
                f"mission_status={self.mission_status}, "
                f"info={self.info}, "
                f"reserved_pos={self.reserved_pos}, "
                f"id_navithor={self.id_navithor}, "
                f"dt_creation={self.dt_creation})"
                )