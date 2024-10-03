from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, History
import hashlib
import datetime
from .authorization import authorized 
import logging
from sqlalchemy import desc

logger = logging.getLogger(__name__)

def generate_md5(username):
    return hashlib.md5(username.encode()).hexdigest()


@app.route('/v1/users')
def test_users():
    return jsonify({'status':True, 'message': 'users OK'}), 200


@app.route('/v1/users/login', methods=['POST', 'OPTIONS'])
def login():
    data = request.get_json()
   
    user = User.query.filter_by(username=data['username'], password=generate_md5(data['password']) ).first()

    if user:
        token = generate_md5(user.username + str(datetime.datetime.now()))
        user.token = token
        user.token_date = datetime.datetime.now()
        db.session.commit()

        History.info("Sistema", f"Operador Logado: {user.username}" )

        return jsonify({'status':True, 'message': 'Logado com sucesso', 'token': token, 'role': user.roles}), 200
    
    return jsonify({'status':False, 'message': 'Credenciais Inválidas'}), 200

@app.route('/v1/users/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user = User.query.filter_by(token=data['token']).first()
    if user:
        user.token = None
        db.session.commit()

        History.info("Sistema", f"Operador Saiu: {user.username}")

        return jsonify({'status':True,'message': 'Deslogado com Sucesso'}), 200
    
    return jsonify({'status':False, 'message': 'Token Invalido'}), 200


@app.route('/v1/users/list', methods=['GET'])
@authorized
def get_all_users(logged_user):
    users = User.query.order_by(desc(User.id)).all()
    user_list = []
    
    if logged_user.roles=="ADMIN":
        # usuario admin ve todos usuarios cadastrados.
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.roles
            }
            user_list.append(user_data)
    else:
        for user in users:
            if logged_user.id==user.id:
                # se usuario nao admin, lista apenas ele proprio.
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.roles
                }
                user_list.append(user_data)

    
    return jsonify({'users': user_list}), 200

@app.route('/v1/users/create', methods=['POST'])
@authorized
def create_user(logged_user):
    logger.info("Solicitado Criação de Usuario")
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'status':False, 'message': 'Ja existe alguem com este login'}), 200
    new_user = User(username=data['username'], password=generate_md5(data['password']), roles=data['roles'])
    db.session.add(new_user)
    db.session.commit()

    History.info("Sistema", f"Operador [{logged_user.username}] criou o usuario [{data['username']}]")

    return jsonify({'status':True, 'message': 'Usuario Criado com sucesso'}), 200


@app.route('/v1/users/update/password', methods=['POST'])
@authorized
def update_password(logged_user):
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({'status':False, 'message': 'Usuario Nao Encontrado'}), 200
    user.password = generate_md5(data['new_password'])
    db.session.commit()

    History.info("Sistema", f"Operador [{logged_user.username}] trocou a senha de [{user.username}]")

    return jsonify({'status':True, 'message': 'Senha Atualizada com Sucesso'}), 200