from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User
import hashlib
import datetime

def generate_md5_token(username):
    return hashlib.md5(username.encode()).hexdigest()

@app.route('/v1/users')
def test_users():
    return jsonify({'message': 'users OK'}), 200


@app.route('/v1/users/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username'], password=data['password']).first()

    if user:
        token = generate_md5_token(user.username + datetime.datetime.now())
        user.token = token
        user.token_date = datetime.datetime.now()
        db.session.commit()
        return jsonify({'message': 'Logado com sucesso', 'token': token, 'roles': user.roles}), 200
    
    return jsonify({'message': 'Credenciais Inválidas'}), 401

@app.route('/v1/users/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user = User.query.filter_by(token=data['token']).first()
    if user:
        user.token = None
        db.session.commit()
        return jsonify({'message': 'Deslogado com Sucesso'}), 200
    
    return jsonify({'message': 'Token Invalido'}), 401


@app.route('/v1/users/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/v1/users/update/password', methods=['POST'])
def update_password():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.password = data['new_password']
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200