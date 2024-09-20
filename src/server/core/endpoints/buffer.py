from flask import Flask, request, jsonify, render_template, Response
from core import db, app
from core.models import User, Mission, History, Buffer
import hashlib
import datetime
import logging
import json
from .authorization import authorized 

logger = logging.getLogger(__name__)

buffer_service = Buffer()

@app.route('/v1/buffers/list', methods=['GET'])
def buffer_list():

    buffer = []

    for bid, data in buffer_service.buffers.items():
        buffer.append(   {
                    "row_id": bid,
                    "description": data["titulo_area"],
                },)

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(buffer, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/buffers/<id_buffer>', methods=['POST'])
def buffer_list_by_id(id_buffer):
    id_buffer = int(id_buffer)
    
    buffer = buffer_service.get_buffer_occupied_by_id(id_buffer)


    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(buffer, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/buffers/<id_buffer>/update/sku/<id_row>/', methods=['POST'])
@authorized
def buffer_sku_update(id_buffer, id_row, logged_user):
    id_buffer = int(id_buffer)
    id_row = int(id_row)
    data = request.get_json()
    
    status = buffer_service.set_sku_to_row(id_buffer, id_row, data["sku"])

    History.info("Sistema", f"Operador [{logged_user.username}] alterou SKU do buffer {id_buffer} linha {id_row} para {data['sku']} ")

    if status:
        return  jsonify({'status': status, "mensage": "Atualizado com sucesso" }), 200
    
    return jsonify({'status': status, "mensage": "Falhou na atualização!" }), 200


@app.route('/v1/buffers/<id_buffer>/update/position/<id_row>/<id_pos>', methods=['POST'])
@authorized
def buffer_pos_update(id_buffer, id_row, id_pos, logged_user):
    id_buffer = int(id_buffer)
    id_row = int(id_row)
    id_pos = int(id_pos)
    data = request.get_json()
    
    status = buffer_service.set_position_occupation(id_buffer, id_row, id_pos, data["occupied"])

    History.info("Sistema", f"Operador [{logged_user.username}] alterou posicao {id_pos} do buffer {id_buffer} linha {id_row} com ocupacao={data['occupied']} ")

    if status:
        return  jsonify({'status': status, "mensage": "Atualizado com sucesso" }), 200
    
    return jsonify({'status': status, "mensage": "Falhou na atualização!" }), 200