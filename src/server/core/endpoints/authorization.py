from flask import Flask, request, jsonify, render_template
from core import db, app
from core.models import User, Mission
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def authorized(fn):
    """Decorator that checks that requests
    contain an id-token in the request header.
    """
    @wraps(fn)
    def _wrap(*args, **kwargs):

        user = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()
            if len(token)==1:
                logger.warning("Authorization Header Invalido!")
                return jsonify({'status':False, 'message': 'Header Invalido. Utilize Authorization: Bearer <SEU_TOKEN>'}), 401
            
            token = token[1]

            # verifica token no banco de dados.
            user = User.query.filter_by(token=token).first()

            if user==None:
                return jsonify({'status':False, 'message': 'Deslogado!'}), 401

        else:
            logger.warning("Header sem Authorization!")
            return jsonify({'status':False, 'message': 'Header sem Authorization'}), 401


        kwargs['logged_user'] = user # se precisar passar como argumento na funcao...

        return fn(*args, **kwargs)

    return _wrap