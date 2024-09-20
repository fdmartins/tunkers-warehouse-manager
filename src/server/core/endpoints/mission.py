from flask import Flask, request, jsonify, render_template, Response
from sqlalchemy import desc
from core import db, app
from core.models import User, Mission
import json
import hashlib
import datetime
import logging

logger = logging.getLogger(__name__)

@app.route('/v1/mission')
def test_mission():
    return jsonify({'message': 'mission OK'}), 200

@app.route('/v1/mission/status/pending', methods=['POST'])
def pending_mission():
    missions = Mission.query.filter(Mission.status!='FINALIZADO').order_by(desc(Mission.id)).all()
    output = [{
        #'id': m.id, 
        'ID Navithor': m.id_server, 
        'ID Local': m.id_local, 
        'Id Step': m.step_id,
        'Status': m.status, 
        'Ação': m.step_type, 
        'Posição Alvo': m.position_target, 
        'Atualizado em': m.dt_updated,
        'Criado em': m.dt_created
        } for m in missions]

    if len(output)==0:
        output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')

@app.route('/v1/mission/status/finish', methods=['POST'])
def finish_mission():
    missions = Mission.query.filter_by(status='FINALIZADO').order_by(desc(Mission.id)).limit(10).all()
    output = [{
        #'id': m.id, 
        'ID Navithor': m.id_server, 
        'ID Local': m.id_local, 
        'Id Step': m.step_id,
        'Status': m.status, 
        'Ação': m.step_type, 
        'Posição Alvo': m.position_target, 
        'Atualizado em': m.dt_updated,
        'Criado em': m.dt_created
        } for m in missions]
    
    if len(output)==0:
        output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')




