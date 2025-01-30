from threading import Thread
import time
from core.models import History
from ..models.mission import Mission
from ..manager.steps_generator import StepsMachineGenerator
from ..protocols.defines import StepType
from ..models.buttons import ButtonCall
import logging
from core import app
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

import json 
import traceback

class MissionControl:
    def __init__(self, db, buffer,  comm):
        self.logger = logging.getLogger(__name__)

        self.logger.info("iniciando Mission Control...")

        self.db = db

        self.comm = comm
        
        self.buffer = buffer

        self.steps_generator = StepsMachineGenerator(db, buffer)

        # inicia thread de monitoramento de chamados.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("Mission Control iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            with app.app_context():
                try:
                    self.run()
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"ERRO GERAL: {e}")
                    self.logger.error(traceback.format_exc())
                    History.error("SISTEMA", f"{e}")
                    time.sleep(20)


                
    def saveSteps(self, id_local, id_server, steps):

        # verificamos quantos indices ja existem para este id_local.
        start_step_index = 0 

        start_step_index = Mission.query.filter(Mission.id_local==id_local).count()

        for id_step in range(len(steps)):
            s = steps[id_step]
            m = Mission(
                id_local = id_local,
                id_server = id_server,
                status = "ENVIADO AO NAVITHOR",
                step_id = start_step_index + id_step,
                step_type = s["StepType"] ,
                
                position_target = s["AllowedTargets"][0]["Id"],
                is_extended = s["Options"]["WaitForExtension"]
            )
            self.db.session.add(m)

        self.db.session.commit()


    def redundantSteps(self, steps):
        return False

    def isStepsAllowed(self, steps):
        # verifica se os proximos passos ja tem alguma posicao em execucao enviado ao navithor.

        positions_steps = []
        for s in steps:
            positions_steps.append(s["AllowedTargets"][0]["Id"])


        if False:
            # NAO USADO APOS IMPLEMENTACAO DE MISSOES EXTENDIDAS
            # proposta 20241205

            # verificamos quais ruas estao reservadas para os movimentos em execucao.
            local_missions = Mission.query.filter(Mission.status!='FINALIZADO').all()

            reserved = []
            for l_m in local_missions:
                #self.logger.info(f"... posicao escalada {l_m.position_target}")
                # buscamos qual areaid e rowid da posicao em execucao...
                area_id, row_id = self.buffer.find_area_and_row_of_position(l_m.position_target)

                # buscamos todas posicoes associadas a esta rua.
                positions = []
                if area_id!=None and row_id!=None:
                    positions = self.buffer.get_row_positions(area_id, row_id)
                
                #self.logger.info(f"posicoes reservadas {positions}")
                # armazenamos todas posicoes reservadas
                for p in positions:
                    reserved.append(p['pos'])

            for p in positions_steps:
                if p in reserved:
                    self.logger.info(f"Missão aguardando finalizar missao em execução em mesma rua de buffer/expedicao - posicoes reservadas {reserved}")
                    return False, "Aguardando finalizar missão em andamento em mesma rua de buffer ou expedição. "



            # para posicoes que nao buffer...
            local_missions = Mission.query.filter(Mission.status!='FINALIZADO').all()
            for l_m in local_missions: 
                if l_m.position_target in positions_steps:
                    return False, f"Aguardando finalizar missão em andamento com mesma posição ({l_m.position_target})"
            

        return True, ""
    
    

    def run(self):
        
        # verificamos chamados botoeiras.
        self.logger.debug("======================================")
        self.logger.debug("verificando chamados das botoeiras")


        button_calls = ButtonCall.query.filter(
                                                or_(
                                                    ButtonCall.mission_status=='PENDENTE',
                                                    ButtonCall.mission_status=='EXECUTANDO',
                                                    ButtonCall.mission_status=='ABORTAR',
                                                )
                                            ).all()
        
        # buscamos missoes na API do navithor.
        navithor_missions = self.comm.get_mission_status() 

        # AQUI ENVIAMOS A MISSAO PRINCIPAL, PODENDO SER A MISSAO COMPLETA OU UMA MISSAO QUE SERA EXTENDIDA.
        for btn_call in button_calls:
            
            try:
                if btn_call.mission_status=="PENDENTE":
                    self.logger.info(f"CHAMADO BOTOEIRA PENDENTE: {btn_call}" )

                is_extension = False

                if btn_call.mission_status=="EXECUTANDO":
                    # Verificamos se a missão esta como WaitingExtension...
                    for nt_m in navithor_missions:
        
                        navithor_id = nt_m["Id"]
                        navithor_main_state = nt_m["State"] #StateEnum (estado geral da missao)

                        local_id = -1
                        try:
                            # missoes criadas diretamente no navithor tem id como string.
                            local_id = int(nt_m["ExternalId"])
                        except:
                            pass

                        if btn_call.id == local_id:
                            # missao da respectiva chamada da botoeira.
                            if  navithor_main_state=="WaitingExtension":
                                is_extension = True
                                break
                    
                    if is_extension==False:
                        # nao há statis de waiting extension...
                        # self.logger.info("Nenhum status de WaitingExtension...")
                        continue
                    else:
                        self.logger.info(f"CHAMADO BOTOEIRA PENDENTE DE EXTENSAO: {btn_call}" )
                        self.logger.info("Missão aguardando WaitingExtension! Complementando passos...")
            
                if btn_call.mission_status=="ABORTAR":
                    # abortamos no navithor...
                    # concluimos o chamado.
                    id_server = self.comm.abort_mission(id_local=btn_call.id)
                    btn_call.mission_status = "FINALIZADO_ERRO"
                    btn_call.info = "Missão abortada pelo operador"
                    self.logger.warning(f"ABORTADA MISSAO id {btn_call.id}")
                    History.warning("SISTEMA", f"MISSAO {btn_call.id} ABORTADA PELO OPERADOR!")
                    continue


                steps = self.steps_generator.get_steps(btn_call)

                print("="*40)
                print(steps)

                # se o destino eh buffer. Verificamos se ja existe algum STEP de missao para a mesma rua. Se sim, aguardamos a conclusão da missao anterior.
                # varremos steps, verificamos se alguma posicao ja foi enviada ao navithor e ainda esta com status diferente de Completed.
                if steps!=None:
                    allowed, message = self.isStepsAllowed(steps)
                    if allowed==False:
                        btn_call.info = message 
                        self.logger.warning("Já existe missão para mesma posição, aguardamos...")
                        steps = None


                if steps==None:
                    self.logger.info("Nenhuma missão a ser enviada.")
                    continue

                # no caso de WaitingExtension, se o navithor não atualizar imediato o status da missão, pode ser que tentamos reenviar.
                # aqui protegemos de reenvio.
                if self.redundantSteps(steps):
                    self.logger.warning("Essas etapas já foram enviadas. Ignorando.")
                    continue

                # enviamos ao navithor. 
                if not is_extension:
                    self.logger.info(f"Enviando Missão ID {btn_call.id}... quantidade de passos {len(steps)}")
                    #self.logger.debug(json.dumps(steps, indent=4) )            
                    id_server = self.comm.send_mission(id_local=btn_call.id, steps=steps)
                else:
                    self.logger.info(f"EXTENDENDO Missão ID {btn_call.id}... quantidade de passos {len(steps)}")
                    id_server = self.comm.extend_mission(id_local=btn_call.id, steps=steps)


                #print(steps)
                # se a missao foi enviada com sucesso. Então armazenamos os steps no banco para acompanhamento de status.
                self.saveSteps(btn_call.id, id_server, steps)
                    
                
                self.logger.info(f"OK Missão ID Navithor: {id_server}")

                # armazenamos no chamado, o id do servidor - ele é usado para monitorar o status das missoes.
                # cuidado, este id é constantamente zerado quando as missoes finalizam. melhor minitorar pelo id local (externalid)
                btn_call.id_navithor = id_server
                btn_call.mission_status = "EXECUTANDO"

            except Exception as e:
                btn_call.mission_status = "FINALIZADO_ERRO"
                btn_call.info = "FALHA - " + str(e)
                self.logger.error(f"ERRO GERAL: {e}")
                self.logger.error(traceback.format_exc())
                History.error("SISTEMA", f"{e}")


        self.db.session.commit()

        self.logger.debug("======================================")