from threading import Thread
import time
from core.models import History
from ..models.mission import Mission

from .steps import STEPS

from .machine_SAMPS import SAMPS
from .machine_RETROFI import RETROFI
from .machine_REENROLADOR import REENROLADOR
from .machine_SPIDER import SPIDER
from .machine_BARRICA import BARRICA
from .machine_CAPACAPA import CAPACAPA
from .machine_EMBALAGEM_MIMI import EMBALAGEM_MIMI
from .machine_EMBALAGEM_K import EMBALAGEM_K

from ..protocols.defines import StepType
from ..models.buttons import ButtonCall
import logging
from core import app
import json 
import traceback

class MissionControl:
    def __init__(self, db, buffer,  comm):
        self.logger = logging.getLogger(__name__)

        self.logger.info("iniciando Mission Control...")

        self.db = db

        self.comm = comm

        self.buffers = buffer

        # maquinas
        self.machine_retrofi = RETROFI(self.db , self.buffers)
        self.machine_samps = SAMPS(self.db , self.buffers)
        self.machine_reenrolador = REENROLADOR(self.db , self.buffers)
        self.machine_spider = SPIDER(self.db , self.buffers)
        self.machine_barrica = BARRICA(self.db , self.buffers)
        self.machine_capacapa = CAPACAPA(self.db , self.buffers)
        self.machine_embalagem_mimi = EMBALAGEM_MIMI(self.db , self.buffers)
        self.machine_embalagem_k = EMBALAGEM_K(self.db , self.buffers)

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
                    time.sleep(2)
                except Exception as e:
                    self.logger.error(f"ERRO GERAL: {e}")
                    self.logger.error(traceback.format_exc())
                    History.error("SISTEMA", f"{e}")
                    time.sleep(10)

                
    def saveSteps(self, id_local, id_server, steps):
        
        for id_step in range(len(steps)):
            s = steps[id_step]
            m = Mission(
                id_local = id_local,
                id_server = id_server,
                status = "ENVIADO AO NAVITHOR",
                step_id = id_step,
                step_type = s["StepType"] ,
                
                position_target = s["AllowedTargets"][0]["Id"]
            )
            self.db.session.add(m)

        self.db.session.commit()

    def isStepsAllowed(self, steps):
        # verifica se os proximos passos ja tem alguma posicao em execucao enviado ao navithor.
        local_missions = Mission.query.filter(Mission.status!='FINALIZADO').all()

        positions_steps = []
        for s in steps:
            positions_steps.append(s["AllowedTargets"][0]["Id"])

        for l_m in local_missions: 
            if l_m.position_target in positions_steps:
                return False

        return True 

    def run(self):
        
        # verificamos chamados botoeiras.
        self.logger.debug("======================================")
        self.logger.debug("verificando chamados das botoeiras")

        button_calls = ButtonCall.query.filter(ButtonCall.mission_status=='PENDENTE').all()

        for btn_call in button_calls:
            self.logger.debug(f"CHAMADO BOTOEIRA PENDENTE: {btn_call}" )
        
            steps = None

            #### AREA A #####

            if btn_call.id_machine in [438,420,419,416,415,422,421,529,528,527,443,439,489]:
                # maquina RETROFILA
                if btn_call.action_type=="RETIRA" and btn_call.situation!="NAO_CONFORME":
                    # carretel cheio na entrada e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_cheio(btn_call)    

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="NAO_CONFORME":
                    # carretel cheio nao conforme e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_nao_conforme(btn_call)   

                elif btn_call.action_type=="ABASTECE_ENTRADA":
                    # carretel cheio na entrada e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio(btn_call)      
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"

            #### AREA B #####

            elif btn_call.id_machine in [6146,6155,6148,6151,6144]:
                # maquinas SAMPS
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_samps.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                    # retira carretel na entrada da maquina
                    steps = self.machine_samps.retira_carretel_nao_conforme(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                    # retira carretel na entrada da maquina
                    steps = self.machine_samps.retira_carretel_errado(btn_call)

                elif btn_call.action_type=="ABASTECE_ENTRADA":
                    # leva carretel na entrada da maquina, mas nao retira vazio.
                    steps = self.machine_samps.so_abastece_carretel(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_samps.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_samps.retira_palete_incompleto(btn_call)

                #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                    # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                    # carrega pallete incompleto na saida.
                #    steps = self.machine_samps.abastece_palete_incompleto(btn_call)
                    
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"
                     

            #### AREA C - REENROLADOR #####

            elif btn_call.id_machine in [6066,6067]:
                if btn_call.action_type=="RETIRA" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_reenrolador.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_reenrolador.retira_palete_incompleto(btn_call)
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"

            #### AREA D - SPIDER #####

            elif btn_call.id_machine in [2015]:
                if btn_call.action_type=="RETIRA" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_spider.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_spider.retira_palete_incompleto(btn_call)
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"

            #### AREA E - BARRICA #####

            elif btn_call.id_machine in [6169,6023,6168]:
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_barrica.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                    # retira carretel na entrada da maquina
                    steps = self.machine_barrica.retira_carretel_nao_conforme(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                    # retira carretel na entrada da maquina
                    steps = self.machine_barrica.retira_carretel_errado(btn_call)

                elif btn_call.action_type=="ABASTECE_ENTRADA":
                    # leva carretel na entrada da maquina, mas nao retira vazio.
                    steps = self.machine_barrica.so_abastece_carretel(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_barrica.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_barrica.retira_palete_incompleto(btn_call)

                #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                    # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                    # carrega pallete incompleto na saida.
                #    steps = self.machine_barrica.abastece_palete_incompleto(btn_call)
                    
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"

            #### AREA F - CAPA CAPA #####

            elif btn_call.id_machine in [6150,6171,6170,6164,6162,6161,6159,6158,6137]:
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_capacapa.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                    # retira carretel na entrada da maquina
                    steps = self.machine_capacapa.retira_carretel_nao_conforme(btn_call)

                elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                    # retira carretel na entrada da maquina
                    steps = self.machine_capacapa.retira_carretel_errado(btn_call)

                elif btn_call.action_type=="ABASTECE_ENTRADA":
                    # leva carretel na entrada da maquina, mas nao retira vazio.
                    steps = self.machine_capacapa.so_abastece_carretel(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_capacapa.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_capacapa.retira_palete_incompleto(btn_call)

                #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                    # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                    # carrega pallete incompleto na saida.
                #    steps = self.machine_capacapa.abastece_palete_incompleto(btn_call)
                    
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"


            #### AREA G - EMBALAGEM MIMI #####

            elif btn_call.id_machine in [2017]:
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_embalagem_mimi.entrega_palete(btn_call)

                elif btn_call.action_type=="RETIRA":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_embalagem_mimi.retira_palete(btn_call)

                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"



            #### AREA K - EMBALAGEM K #####

            elif btn_call.id_machine in [1787]:
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_embalagem_k.entrega_palete(btn_call)

                elif btn_call.action_type=="RETIRA":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_embalagem_k.retira_palete(btn_call)

                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                    btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                    btn_call.mission_status = "FINALIZADO_ERRO"

            else:
                self.logger.error(f"Maquina {btn_call.id_machine} não existe")
                btn_call.info = f"Maquina {btn_call.id_machine} não existe"
                btn_call.mission_status = "FINALIZADO_ERRO"

            # se o destino eh buffer. Verificamos se ja existe algum STEP de missao para a mesma rua. Se sim, aguardamos a conclusão da missao anterior.
            # varremos steps, verificamos se alguma posicao ja foi enviada ao navithor e ainda esta com status diferente de Completed.
            if self.isStepsAllowed(steps)==False:
                btn_call.info = f"Aguardando finalizar missão anterior com posições coincidentes..."
                self.logger.warning("Já existe missão para mesma posição, aguardamos...")
                steps = None


            if steps==None:
                self.logger.info("Nenhuma missão a ser enviada.")
                continue

            # enviamos ao navithor. 

            self.logger.info(f"Enviando Missão ID {btn_call.id}... quantidade de passos {len(steps)}")
            #self.logger.debug(json.dumps(steps, indent=4) )            
            id_server = self.comm.send_mission(id_local=btn_call.id, steps=steps)

            #print(steps)
            # se a missao foi enviada com sucesso. Então armazenamos os steps no banco para acompanhamento de status.
            self.saveSteps(btn_call.id, id_server, steps)
                
            
            self.logger.info(f"OK Missão ID Navithor: {id_server}")

            # armazenamos no chamado, o id do servidor - ele é usado para monitorar o status das missoes.
            # cuidado, este id é constantamente zerado quando as missoes finalizam. melhor minitorar pelo id local (externalid)
            btn_call.id_navithor = id_server
            btn_call.mission_status = "EXECUTANDO"

        self.db.session.commit()

        self.logger.debug("======================================")