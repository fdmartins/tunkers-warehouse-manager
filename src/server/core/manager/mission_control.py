from threading import Thread
import time

from ..protocols.defines import StepType
from ..models.buttons import ButtonCall

import logging
from core import app

class MissionControl:
    def __init__(self, db, buffer,  comm):
        self.logger = logging.getLogger(__name__)

        self.logger.info("iniciando Mission Control...")

        self.db = db

        self.comm = comm

        self.buffers = buffer

        # carrega posicoes/tags de cada maquina.
        self.machines_requests = {
            1: {
                "ABASTECE": {"POS": 5000, "BUFFERS_ALLOWED": [1,2]} , 
                "RETIRA":   {"POS": 5010, "BUFFERS_ALLOWED": [2]} ,   
                },
            2: {
                "ABASTECE": {"POS": 6000, "BUFFERS_ALLOWED": [1,2]} , 
                "RETIRA":   {"POS": 6010, "BUFFERS_ALLOWED": [1,2]} , 
                }
        }

        # inicia thread.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("Mission Control iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            try:
                with app.app_context():
                    self.run()
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"ERRO GERAL: {e}")
                time.sleep(10)

            
    def get_pos_from_machine_by_id_and_action(self, machine_id, action):
        pos =  self.machines_requests[machine_id][action]["POS"]
        buffers_allowed = self.machines_requests[machine_id][action]["BUFFERS_ALLOWED"]
        return pos, buffers_allowed

    def run(self):
        
        # verificamos chamados botoeiras.
        self.logger.debug("======================================")
        self.logger.debug("verificando chamados das botoeiras")

        button_calls = ButtonCall.query.filter(ButtonCall.mission_status=='PENDENTE').all()

        for btn_call in button_calls:
            self.logger.debug(f"CHAMADO BOTOEIRA PENDENTE: {btn_call}" )
        
            # SE DESCARGA / ENTRADA MAQUINA:
            #       MISSAO: Buscar o SKU desejado no BUFFER e Descarregar na maquina. Setar WaitForExtension
            # SE CARGA / SAIDA MAQUINA:
            #       Manter pendente se tem chamado botoeira para DESCARGA na entrada da mesma maquina.
            #       MISSAO: Enviar missao como extension com CARGA NA SAIDA e descarga no BUFFER. Na missão que esta com WaitingExtension na mesma maquina.
            #       Não existe chamado botoeira para descarga. Nem missao com WaitingExtension. Então, MISSAO: para retirar CARGA NA SAIDA e descarga no BUFFER.

            pos_load = None
            pos_unload = None
            extension_of = None

            if btn_call.action_type=="ABASTECE":
                # entrada de maquina.
                
                pos_unload, buffers_allowed= self.get_pos_from_machine_by_id_and_action(btn_call.id_machine, "ABASTECE")

                # verificamos qual posicao tem o SKU.
                tag_pos_sku, area_id_sku = self.buffers.get_last_pos_of_sku(btn_call.sku, buffers_allowed)

                if tag_pos_sku == None:
                    # nao existe sku no buffer.
                    # nao devemos entrar nunca aqui, pois tratamos isso logo no chamado.
                    self.logger.error(f"Não existe sku {btn_call.sku} solicitado pela maquina {btn_call.id_machine} - POR QUE ESTAMOS AQUI!?!? ")
                    continue
                else:
                    pos_load = tag_pos_sku
                    
                    self.logger.debug(f"Encontrado posicao {pos_unload} para acao ABASTECE na maquina {btn_call.id_machine} ")
                    self.logger.info(f"Encontramos o sku na posicao {tag_pos_sku} do buffer id {area_id_sku} , moveremos para posicao {pos_unload}")      

            elif btn_call.action_type=="RETIRA":
                # saida da maquina.
                # verificamos se tem chamado de ABASTECE na mesma maquina 
                # PREMISSA para fazer o ciclo completo: Primeiro deve ter chamado de ABASTECE, depois RETIRA.
                ret = ButtonCall.query.filter(
                    ButtonCall.mission_status.in_(["EXECUTANDO", "PENDENTE"]), 
                    ButtonCall.id_machine==btn_call.id_machine,
                    ButtonCall.action_type=="ABASTECE",
                    ButtonCall.id != btn_call.id).one_or_none()
                
                if ret!=None:
                    # existe missao. Enviamos como extensao da atual.
                    self.logger.info(f"Criando passo de missão extendida do chamado {ret.id}, pois encontrei chamado para ABASTECER a mesma maquina {btn_call.id_machine}. ")
                    extension_of = ret.id
                    
                # nao existe missao. Entao executamos como missao unica.
                pos_load, buffers_allowed = self.get_pos_from_machine_by_id_and_action(btn_call.id_machine, "RETIRA")
                self.logger.debug(f"Encontrado posicao {pos_load} para acao RETIRA na maquina {btn_call.id_machine} ")

                # buscamos proxima posicao vazia no buffer. 
                self.logger.debug(f"Procurando posicao no buffer para sku {btn_call.sku}")
                tag_pos_sku, area_id_sku  = self.buffers.get_free_pos(btn_call.sku, buffers_allowed)

                if tag_pos_sku == None:
                    self.logger.error(f"Não foi possivel encontrar posicao no buffer para o sku {btn_call.sku} ")
                    continue
                else:
                    self.logger.debug(f"Encontrado posicao {tag_pos_sku} no buffer {area_id_sku} para sku {btn_call.sku}")
                    pos_unload = tag_pos_sku

            else:
                raise Exception(f"action_type nao esperado: {btn_call.action_type}")


            # se o destino eh buffer. Verificamos se ja existe algum STEP de missao para a mesma rua. Se sim, aguardamos a conclusão da missao anterior.
            # CORRIGIR. Precisa verificar em STEPS.
            #ret = ButtonCall.query.filter(
            #        ButtonCall.mission_status.in_(["EXECUTANDO", "PENDENTE"]), 
            #        ButtonCall.id != btn_call.id).all()
            #for r in ret:
            #    self.buffers.get_buffer_info_from_pos(r)


            # montamos os passos da missão.

            self.logger.info(f"Enviando Missão para Carregar em {pos_load} Descarregar em {pos_unload}")

            steps = [  # passos de execucao da missao.
                {
                    "StepType": StepType.Pickup.value, # acao de carga Enum StepType
                    "Options": {
                        #"Load": {
                        #    "RequiredLoadStatus": "LoadAtLocation",
                        #    "RequiredLoadType": 2
                        #},
                        "SortingRules": ["Priority", "Closest"]
                    },
                    "AllowedTargets": [  # vai para qualquer uma dessas posicoes, priorizando prioridade e proximidade.
                        {"Id": pos_load},
                    ],
                    "AllowedWaits": [ # se os targets estiverem ocupados/reservados, pode aguardar nessas posicoes..
                       # {"Id": 16}
                    ]
                },

                {
                    "StepType": StepType.Dropoff.value, # acao de carga Enum StepType
                    "Options": {
                        #"Load": {
                        #    "RequiredLoadStatus": "LoadAtLocation",
                        #    "RequiredLoadType": 2
                        #},
                        "SortingRules": ["Priority", "Closest"],
                        "WaitForExtension": True
                    },
                    "AllowedTargets": [  # vai para qualquer uma dessas posicoes, priorizando prioridade e proximidade.
                        {"Id": pos_unload},
                    ],
                    "AllowedWaits": [ # se os targets estiverem ocupados/reservados, pode aguardar nessas posicoes..
                       # {"Id": 16}
                    ]
                },
            ]


            # enviamos ao navithor.
            if extension_of==None:
                self.logger.info(f"Enviando Missão ID {btn_call.id}...")
                id_server = self.comm.send_mission(id_local=btn_call.id, steps=steps)
            else:
                self.logger.info(f"Extendendo Missão ID {extension_of}...")
                id_server = self.comm.extend_mission(extension_of, steps=steps)
                
            
            self.logger.info(f"OK Missão ID Navithor: {id_server}")

            # armazenamos no chamado, o id do servidor - ele é usado para monitorar o status das missoes.
            # cuidado, este id é constantamente zerado quando as missoes finalizam. melhor minitorar pelo id local (externalid)
            btn_call.id_navithor = id_server
            btn_call.mission_status = "EXECUTANDO"

        self.db.session.commit()

        self.logger.debug("======================================")