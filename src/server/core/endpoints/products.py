from flask import Flask, request, jsonify, render_template, Response
from sqlalchemy import desc, asc
from core import db, app
from core.models import History, ProdutosCompleto, ProdutosResumido
import json
import hashlib
import datetime
import logging
from flask import Blueprint
from .authorization import authorized 

def register_products_routes():
    logger = logging.getLogger(__name__)

    @app.route('/v1/products')
    def test_products():
        return jsonify({'message': 'products OK'}), 200


    @app.route('/v1/products/complete', methods=['GET'])
    def products_list_complete():

        products = ProdutosCompleto.query.order_by(asc(ProdutosCompleto.nome)).all()

        output = []
        for c in products:
            output.append({
                'id': c.id,
                'sku': c.sku,
                'nome': c.nome,
                'tipo': c.tipo,
            })


        # Usa json.dumps para garantir a ordem das chaves como informado acima.
        json_output = json.dumps(output, default=str, indent=4)

        # Retorna a resposta como um Response para garantir a ordem das chaves
        return Response(json_output, mimetype='application/json')

    @app.route('/v1/products/summarized', methods=['GET'])
    def products_list_summarized():
        
        products = ProdutosResumido.query.order_by(asc(ProdutosResumido.bitola)).all()
        
        output = []
        for c in products:
            output.append({
                'id': c.id,
                'bitola': c.bitola,
                'nome': c.nome,
                'sku': c.sku,
                'tipo': c.tipo,
            })


        # Usa json.dumps para garantir a ordem das chaves como informado acima.
        json_output = json.dumps(output, default=str, indent=4)

        # Retorna a resposta como um Response para garantir a ordem das chaves
        return Response(json_output, mimetype='application/json')


    @app.route('/v1/products/new/complete', methods=['POST'])
    @authorized
    def products_new_complete(logged_user):
        data = request.get_json()

        p = ProdutosCompleto.query.filter_by(sku=data['sku']).first()

        if p!=None:
            return jsonify({'status':False, 'message': 'SKU DUPLICADO'}), 409

        new_p = ProdutosCompleto(sku=data['sku'], nome=data['nome'], tipo=data['tipo'] )
        db.session.add(new_p)
        db.session.commit()

        History.info("Sistema", f"Operador  [{logged_user.username}] criou novo ProdutosCompleto sku {new_p.sku} {new_p.nome} {new_p.tipo}")

        return jsonify({'status':True, 'message': 'Produto Criado com Sucesso'}), 200


    @app.route('/v1/products/new/summarized', methods=['POST'])
    @authorized
    def products_new_summarized(logged_user):
        data = request.get_json()

        p = ProdutosResumido.query.filter_by(sku=data['sku']).first()

        if p!=None:
            return jsonify({'status':False, 'message': 'SKU DUPLICADO'}), 409

        new_p = ProdutosResumido(bitola=data['bitola'],  nome=data['nome'],  sku=data['sku'], tipo=data['tipo'] )
        db.session.add(new_p)
        db.session.commit()

        History.info("Sistema", f"Operador  [{logged_user.username}] criou novo ProdutosResumido sku {new_p.sku} {new_p.bitola} {new_p.nome} {new_p.tipo}")

        return jsonify({'status':True, 'message': 'Produto Criado com Sucesso'}), 200



    @app.route('/v1/products/delete/complete/<id>', methods=['POST'])
    @authorized
    def products_remove_complete(id, logged_user):

        p = ProdutosCompleto.query.filter_by(id=id).first()

        if p==None:
            return jsonify({'status':False, 'message': 'Produto não existe'}), 404


        db.session.delete(p)
        db.session.commit()

        History.info("Sistema", f"Operador  [{logged_user.username}] Removeu ProdutosCompleto sku {p.sku} {p.nome} {p.tipo}")

        return jsonify({'status':True, 'message': 'Produto Removido com Sucesso'}), 200

    @app.route('/v1/products/delete/summarized/<id>', methods=['POST'])
    @authorized
    def products_remove_summarized(id, logged_user):

        p = ProdutosResumido.query.filter_by(id=id).first()

        if p==None:
            return jsonify({'status':False, 'message': 'Produto não existe'}), 404
        
        db.session.delete(p)
        db.session.commit()

        History.info("Sistema", f"Operador [{logged_user.username}] Removeu ProdutosResumido sku {p.sku} {p.nome} {p.tipo}")

        return jsonify({'status':True, 'message': 'Produto Removido com Sucesso'}), 200
