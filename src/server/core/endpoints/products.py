from flask import Flask, request, jsonify, render_template, Response
from sqlalchemy import desc, asc
from core import db, app
from core.models import User, Mission
import json
import hashlib
import datetime
import logging

logger = logging.getLogger(__name__)

@app.route('/v1/products')
def test_products():
    return jsonify({'message': 'products OK'}), 200


@app.route('/v1/products/complete', methods=['GET'])
def products_list_complete():

    output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')

@app.route('/v1/products/new/complete', methods=['POST'])
def products_new_complete():

    output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/products/summarized', methods=['GET'])
def products_list_summarized():

    output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/products/new/summarized', methods=['POST'])
def products_new_summarized():
    output = [{}]

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')



