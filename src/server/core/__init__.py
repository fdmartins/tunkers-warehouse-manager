
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS, cross_origin



app = Flask(__name__)

# Habilitar CORS apenas para uma origem específica
CORS(app, resources={r"/v1/*": {"origins": "http://127.0.0.1:8080"}})


#app.config.from_object('config')
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_tunkers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def start():
    from core import endpoints
    from core import manager
    from core import models
    from .models.buffers import Buffer
    from .protocols.navithor import Navithor

    comm = Navithor()
    buffers = Buffer()

    sc = manager.StatusControl(db, comm)

    mc = manager.MissionControl(db, buffers,  comm)



