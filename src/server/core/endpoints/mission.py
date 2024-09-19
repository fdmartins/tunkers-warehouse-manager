from flask import Flask, request, jsonify, render_template, Response
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
    missions = Mission.query.filter(Mission.status!='Completed').all()
    output = [{
        #'id': m.id, 
        'ID Navithor': m.id_server, 
        'ID Local': m.id_local, 
        'Status': m.status, 
        'Ação Atual': m.current_step_type, 
        'Atualizado em': m.dt_updated,
        'Criado em': m.dt_created
        } for m in missions]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')

@app.route('/v1/mission/status/finish', methods=['POST'])
def finish_mission():
    missions = Mission.query.filter_by(status='Completed').all()
    output = [{
        #'id': m.id, 
        'ID Navithor': m.id_server, 
        'ID Local': m.id_local, 
        'Status': m.status, 
        'Passo Atual': m.current_step,
        'Ação': m.step_type,
        'Posição Alvo': m.positions_target,
        'Atualizado em': m.dt_updated,
        'Criado em': m.dt_created
        } for m in missions]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')




