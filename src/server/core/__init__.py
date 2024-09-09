
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)

#app.config.from_object('config')
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_tunkers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def start():
    from core import endpoints
    from core import manager
    from core import models

    sc = manager.StatusControl(db)

    mc = manager.MissionControl(db)



