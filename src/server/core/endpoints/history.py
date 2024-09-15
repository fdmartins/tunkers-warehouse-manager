from flask import Flask, request, jsonify, render_template, Response
from core import db, app
from core.models import User, Mission, History
import hashlib
import datetime
import logging
import json
from sqlalchemy import desc

logger = logging.getLogger(__name__)

@app.route('/v1/history/alerts', methods=['POST'])
def last_alerts():
    alerts = History.query.filter_by(level='ERRO').order_by(desc(History.id)).all()
    output = []
    for a in alerts:
        output.append({
            'Horário': a.dt_created,
            'Tipo': a.alert_type,
            'Nível': a.level,
            'Mensagem': a.message,

        })

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/history/list', methods=['POST'])
def history_list():
    alerts = History.query.order_by(desc(History.id)).all()
    output = []
    for a in alerts:
        output.append({
            'Horário': a.dt_created,
            'Tipo': a.alert_type,
            'Nível': a.level,
            'Mensagem': a.message,
        })

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')
