
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS, cross_origin
import configparser
from .utils import FileRef

#print(FileRef.get_path('templates'))
#exit()

app = Flask(__name__, template_folder=FileRef.get_path('templates'), static_folder=FileRef.get_path('static') )

# Habilitar CORS apenas para uma origem específica
CORS(app, resources={r"/v1/*": {"origins": "http://127.0.0.1:8080"}})


#app.config.from_object('config')
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + FileRef.get_path('instance/gerenciador_tunkers.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def start():
    from core import endpoints
    from core import manager
    from core import models
    from .models.buffers import Buffer
    from .protocols.navithor import Navithor

    comm = Navithor()
    buffers = Buffer(comm)
    
    endpoints.create_endpoints(buffers)

    sc = manager.StatusControl(db, buffers, comm)

    mc = manager.MissionControl(db, buffers,  comm)



