from flask import Flask, request, jsonify, render_template, Response
from core import db, app
from core.models import ButtonCall, ButtonStatus
import hashlib
from datetime import datetime
import logging
import json
from sqlalchemy import desc

logger = logging.getLogger(__name__)

@app.route('/v1/button')
def test_buttons():
    return jsonify({'message': 'buttons OK'}), 200


@app.route('/v1/button/call/list', methods=['POST'])
def list_call():
    bt_calls = ButtonCall.query.order_by(desc(ButtonCall.id)).all()
    # Formata a saída para visualização
    output = []
    for c in bt_calls:
        output.append({
            'ID': c.id,
            #'Botoeira': c.ip_device,
            'Máquina': c.id_machine,
            'Material': c.material_type,
            'Tipo Ação': c.action_type,
            'Situação': c.situation,
            'SKU': c.sku,
            #'Bitola': c.gauge,
            #'Produto': c.product,
            'Status': c.mission_status,
            'Info': c.info, 
            'Dt Chamada': c.dt_creation
        })

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')


@app.route('/v1/button/call', methods=['POST'])
def create_call():
    data = request.get_json()

    message_type = data.get('message_type')
    ip_device = request.remote_addr 

    # Tenta encontrar o registro pelo ip_device
    button_status_db = ButtonStatus.query.filter_by(ip_device=ip_device).first()

    if button_status_db==None:
        # nao existe ainda.
        button_status = ButtonStatus(
            ip_device=ip_device,
            last_call=datetime.now(),
            last_life=datetime.now(),
            life_sequence=0,
            life_previous_sequence=-1
        )
        db.session.add(button_status)
        db.session.commit()

        logger.warning(f"Inserido nova botoeira {ip_device} no banco.") 

        # garantido que agora existe.
        button_status_db = ButtonStatus.query.filter_by(ip_device=ip_device).first()


    if message_type=="LIFE":
        sequence = data.get('sequence')
        logger.debug(f"Recebido LIFE botoeira {ip_device} - seq:{sequence} seq_anterior:{button_status_db.life_sequence} ")

        button_status_db.last_life = datetime.now()
        button_status_db.life_previous_sequence = button_status_db.life_sequence
        button_status_db.life_sequence = sequence

        db.session.commit()

        return jsonify({}), 200
    
    elif message_type=="ACTION":

        try:
    
            material_type = data.get('material_type')
            action_type = data.get('action_type')
            situation = data.get('situation')
            id_machine = data.get('id_machine')

            sku = data.get('sku')

            # se enviou sku, fazemos o resolver pela nossa tabela...
            if sku==None:
                gauge = data.get('gauge')
                product = data.get('product')
            else:
                gauge = ""
                product = ""
            

            new_call = ButtonCall(
                ip_device=ip_device,
                message_type=message_type,
                material_type=material_type,
                action_type=action_type,
                situation=situation,
                id_machine=id_machine,
                sku=sku,
                gauge=gauge,
                product=product,
                mission_status="PENDENTE",
                dt_creation=datetime.now()  
            )

            logger.debug(f"Recebido ACAO botoeira {new_call} ")

            # Verificamos se este IP esta na whitelist.
            # TODO

            # Verificamos se existe algum chamado pendente para a mesma maquina.
            # TODO



            if False:
                logger.warning(f"Ação NEGADA. Já existe chamado. ")
                return jsonify({'status': False, "message":f"NEGADO. Ja existe chamado." }), 200

            # atualiza na tabela de status o ultimo horario da ordem.
            button_status_db.last_call = datetime.now()

            # Adicionar a chamada ao banco de dados
            db.session.add(new_call)
            db.session.commit()


            logger.info(f"Ação aceita. Cadastrada no Banco.")

            return jsonify({'status': True, "message":f"Confirmado!" }), 200

        except Exception as e:
            logger.error(f"Erro Geral: {e}")
            return jsonify({'status': False, "message":f"Erro Geral: {e} " }), 200

    else:
        return jsonify({'status': False, "message":f"tipo {message_type} invalido" }), 200


@app.route('/v1/button/comm', methods=['POST'])
def list_comm():
    bt_status = ButtonStatus.query.order_by(desc(ButtonStatus.ip_device)).all()
    # Formata a saída para visualização
    output = []
    for c in bt_status:
        output.append({
            'Botoeira': c.ip_device,
            'Status': c.status_message,
            'Último Chamado': c.last_call,
            'Última Comunicação': c.last_life,
        })

    # Usa json.dumps para garantir a ordem das chaves como informado acima.
    json_output = json.dumps(output, default=str, indent=4)

    # Retorna a resposta como um Response para garantir a ordem das chaves
    return Response(json_output, mimetype='application/json')