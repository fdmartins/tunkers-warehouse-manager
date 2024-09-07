from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, Mission
import hashlib
import datetime

@app.route('/v1/mission')
def test_mission():
    return jsonify({'message': 'mission OK'}), 200

@app.route('/v1/mission/status/pending', methods=['GET'])
def pending_mission():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token missing'}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    missions = Mission.query.filter_by(user_id=user.id, status='pending').all()
    return jsonify([{'id': m.id, 'status': m.status, 'last_update': m.last_update} for m in missions]), 200

@app.route('/v1/mission/finish', methods=['POST'])
def finish_mission():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token missing'}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()
    mission = Mission.query.filter_by(id=data['mission_id'], user_id=user.id).first()
    if mission:
        mission.status = 'finished'
        mission.last_update = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Mission finished'}), 200
    return jsonify({'message': 'Mission not found'}), 404

@app.route('/v1/mission/last', methods=['GET'])
def last_mission():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token missing'}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    mission = Mission.query.filter_by(user_id=user.id).order_by(Mission.last_update.desc()).first()
    if mission:
        return jsonify({'id': mission.id, 'status': mission.status, 'last_update': mission.last_update}), 200
    return jsonify({'message': 'No missions found'}), 404



