from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, Mission
import hashlib
import datetime
import logging

logger = logging.getLogger(__name__)

@app.route('/v1/mission')
def test_mission():
    return jsonify({'message': 'mission OK'}), 200

@app.route('/v1/mission/status/pending', methods=['POST'])
def pending_mission():
    missions = Mission.query.filter_by(status='PENDENTE').all()
    return jsonify([{'id': m.id, 'status': m.status, 'last_update': m.last_update} for m in missions]), 200

@app.route('/v1/mission/status/finish', methods=['POST'])
def finish_mission():
    missions = Mission.query.filter_by(status='FINALIZADO').all()
    return jsonify([{'id': m.id, 'status': m.status, 'last_update': m.last_update} for m in missions]), 200


