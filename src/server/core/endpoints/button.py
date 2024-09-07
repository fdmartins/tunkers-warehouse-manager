from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, Mission
import hashlib
import datetime

@app.route('/v1/button')
def test_buttons():
    return jsonify({'message': 'buttons OK'}), 200

@app.route('/v1/button/call', methods=['POST'])
def create_call():
    data = request.get_json()

    return jsonify({}), 200