from flask import Flask, request, jsonify, render_template, Response
from core import db, app
from core.models import ButtonCall, ButtonStatus, Buffer, ProdutosCompleto, ProdutosResumido
import hashlib
from datetime import datetime
import logging
import json
from sqlalchemy import desc, asc
from ..manager.steps_generator import StepsMachineGenerator
import traceback
from flask import Blueprint


def register_button_routes(buffer_service):
    logger = logging.getLogger(__name__)
    #buffer_service = Buffer()
    steps_generator = StepsMachineGenerator(db, buffer_service)

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
                'ID Botoeira': c.id_button,
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



    @app.route('/v1/button/call/abort/<id>', methods=['POST'])
    def abort_call(id):

        call_ret = ButtonCall.query.filter_by(id=id).first()
        
        if call_ret==None:
            return jsonify({'status': False, "message":f"Chamado nao existe!" }), 404
        
        call_ret.mission_status = "ABORTAR"

        db.session.commit()

        return jsonify({'status': True, "message":f"Abortando..." }), 200




    @app.route('/v1/button/call', methods=['POST'])
    def create_call():
        data = request.get_json()

        message_type = data.get('message_type')
        ip_device = request.remote_addr 

        # Tenta encontrar o registro pelo ip_device
        button_status_db = ButtonStatus.query.filter_by(ip_device=ip_device).first()

        if button_status_db==None and ip_device!="127.0.0.1":
            
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


        if message_type=="LIFE" and ip_device!="127.0.0.1":
            sequence = data.get('sequence')
            logger.debug(f"Recebido LIFE botoeira {ip_device} - seq:{sequence} seq_anterior:{button_status_db.life_sequence} ")

            button_status_db.last_life = datetime.now()
            button_status_db.life_previous_sequence = button_status_db.life_sequence
            button_status_db.life_sequence = sequence

            db.session.commit()

            return jsonify({}), 200
        
        elif message_type=="ACTION":

            try:
                id_button = data.get('id_button')
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
                    id_button=id_button,
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

                # verificamos se existe chamado PENDENTE ou EXECUTANDO para essa maquina...
                # implementado no get_steps...

                # Verificamos se pode fazer o chamado.
                _ = steps_generator.get_steps(new_call, pre_check=True)

                # atualiza na tabela de status o ultimo horario da ordem.
                if ip_device!="127.0.0.1":
                    button_status_db.last_call = datetime.now()

                # Adicionar a chamada ao banco de dados
                # para fins de registro, será adicionado mesmo se deu erro
                db.session.add(new_call)
                db.session.commit()

                if new_call.mission_status!="PENDENTE":
                    # generator mudou o status. Isso significa que recusou. Retornamos a falha.
                    logger.warning(f"Chamado Recusado! Motivo: " + new_call.mission_status)
                    return jsonify({'status': False, "message":f"RECUSADO: {new_call.info}" }), 200

                logger.info(f"Ação aceita. Cadastrada no Banco.")

                return jsonify({'status': True, "message":f"Confirmado!" }), 200

            except Exception as e:
                logger.error(f"Erro Geral: {e}")
                logger.error(traceback.format_exc())
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



    @app.route('/v1/button/config/produtos.json', methods=['GET'])
    def config_produtos_resumido():
        """
        {
            "Produtos": {
    
            "0,8": {
                "BE14   ": {
                "SKU": "40478932",
                "material_type": "BOBINA"
                }
            },

            }
        }
        """

        products = ProdutosResumido.query.order_by(asc(ProdutosResumido.bitola)).all()

        output = {"Produtos": {}}

        for p in products:
            output["Produtos"].setdefault(p.bitola, {})
            output["Produtos"][p.bitola].setdefault(p.nome, {})
            output["Produtos"][p.bitola][p.nome]["SKU"] = p.sku
            output["Produtos"][p.bitola][p.nome]["material_type"] = p.tipo

        # Usa json.dumps para garantir a ordem das chaves como informado acima.
        json_output = json.dumps(output, default=str, indent=4)

        # Retorna a resposta como um Response para garantir a ordem das chaves
        return Response(json_output, mimetype='application/json')


    @app.route('/v1/button/config/qrcodeprod.json', methods=['GET'])
    def config_produtos_completo():
        """
        {
            "Produtos": {
            
                "40479024": {"Nome":"AR RETR COB 0,79MM BE14","material_type": "BOBINA"},
                "40478932": {"Nome":"AR RETR COB 0,80MM BE14","material_type": "BOBINA"},
                "40479135": {"Nome":"AR RETR COB 0,89MM BE14","material_type": "BOBINA"},

            }
        }
        """

        products = ProdutosCompleto.query.order_by(asc(ProdutosCompleto.nome)).all()

        output = {"Produtos": {}}

        for p in products:
            output["Produtos"].setdefault(p.sku, {})
            output["Produtos"][p.sku]["Nome"] = p.nome
            output["Produtos"][p.sku]["material_type"] = p.tipo

        # Usa json.dumps para garantir a ordem das chaves como informado acima.
        json_output = json.dumps(output, default=str, indent=4)

        # Retorna a resposta como um Response para garantir a ordem das chaves
        return Response(json_output, mimetype='application/json')
