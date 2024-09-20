from threading import Thread
import time

from ..models.mission import Mission

from .steps import STEPS

from .machine_SAMPS import SAMPS
from .machine_RETROFI import RETROFI

from ..protocols.defines import StepType
from ..models.buttons import ButtonCall
import logging
from core import app
import json 


class MissionControl:
    def __init__(self, db, buffer,  comm):
        self.logger = logging.getLogger(__name__)

        self.logger.info("iniciando Mission Control...")

        self.db = db

        self.comm = comm

        self.buffers = buffer

        self.machine_retrofi = RETROFI(self.db , self.buffers)
        self.machine_samps = SAMPS(self.db , self.buffers)
        

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

    def run(self):
        
        # verificamos chamados botoeiras.
        self.logger.debug("======================================")
        self.logger.debug("verificando chamados das botoeiras")

        button_calls = ButtonCall.query.filter(ButtonCall.mission_status=='PENDENTE').all()

        for btn_call in button_calls:
            self.logger.debug(f"CHAMADO BOTOEIRA PENDENTE: {btn_call}" )
        
            steps = None

            if btn_call.id_machine in [438,420,419,416,415,422,421,529,528,527,443,439,489]:
                # maquina RETRIFILA
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_cheio(btn_call)    

                if btn_call.action_type=="NAO_CONFORME":
                    # carretel cheio nao conforme e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_nao_conforme(btn_call)   

                if btn_call.action_type=="ABASTECE_ENTRADA":
                    # carretel cheio na entrada e retira carretel vazio
                    steps = self.machine_retrofi.abastece_carretel_vazio(btn_call)      


            if btn_call.id_machine in [6146,6155,6148,6151,6144]:
                # maquinas SAMPS
                if btn_call.action_type=="ABASTECE":
                    # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                    steps = self.machine_samps.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="NAO_CONFORME":
                    # retira carretel na entrada da maquina
                    steps = self.machine_samps.retira_carretel_nao_conforme(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="ERRADO":
                    # retira carretel na entrada da maquina
                    steps = self.machine_samps.retira_carretel_errado(btn_call)

                elif btn_call.action_type=="ABASTECE_ENTRADA":
                    # leva carretel na entrada da maquina, mas nao retira vazio.
                    steps = self.machine_samps.so_abastece_carretel(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="COMPLETO":
                    # retira palete completo na saida.
                    steps = self.machine_samps.retira_palete(btn_call)

                elif btn_call.action_type=="RETIRA" and btn_call.situation=="INCOMPLETO":
                    # retira palete incompleto na saida.
                    steps = self.machine_samps.retira_palete_incompleto(btn_call)

                elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                    # carrega pallete incompleto na saida.
                    steps = self.machine_samps.abastece_palete_incompleto(btn_call)
                    
                else:
                    self.logger.error(f"Acao da botoeira invalida {btn_call.action_type}")
                    # TODO - cancelamos o chamado
                     


            # se o destino eh buffer. Verificamos se ja existe algum STEP de missao para a mesma rua. Se sim, aguardamos a conclusão da missao anterior.
            # Segundo ademilson, o navithor garante sequenciamento de trafego, então vamos ignorar esse trtamento no momento.


            if steps==None:
                self.logger.info("Nenhuma missão a ser enviada.")
                continue

            # enviamos ao navithor.

            self.logger.info(f"Enviando Missão ID {btn_call.id}...")
            #self.logger.debug(json.dumps(steps, indent=4) )            
            id_server = self.comm.send_mission(id_local=btn_call.id, steps=steps)

            # se a missao foi enviada com sucesso. Então armazenamos os steps no banco para acompanhamento de status.
            self.saveSteps(btn_call.id, id_server, steps)
                
            
            self.logger.info(f"OK Missão ID Navithor: {id_server}")

            # armazenamos no chamado, o id do servidor - ele é usado para monitorar o status das missoes.
            # cuidado, este id é constantamente zerado quando as missoes finalizam. melhor minitorar pelo id local (externalid)
            btn_call.id_navithor = id_server
            btn_call.mission_status = "EXECUTANDO"

        self.db.session.commit()

        self.logger.debug("======================================")