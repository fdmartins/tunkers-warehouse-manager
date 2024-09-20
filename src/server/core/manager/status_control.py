from threading import Thread

from ..models.mission import Mission

from ..protocols.navithor import Navithor
from ..models.buttons import ButtonCall, ButtonStatus
import time
import logging
from datetime import datetime, timedelta
from core import app

class StatusControl:
    def __init__(self, db, buffers, comm):
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Iniciando StatusControl...")

        self.db = db
        self.buffers = buffers
        self.comm = comm

        self.last_token_navithor_update = None

        

        # inicia thread.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("StatusControl Iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            try:
                with app.app_context():
                    self.checkAuthTokenNavithor()
                    self.checkButtonStatus()
                    self.checkMissionStatus()
                    time.sleep(2)
            except Exception as e:
                self.logger.error(f"ERRO GERAL: {e}")
                time.sleep(10)


    def checkAuthTokenNavithor(self):
        # o token tem tempo de validade.
        # renovamos a cada 1h.
        if self.last_token_navithor_update==None or (datetime.now() - self.last_token_navithor_update) > timedelta(hours=1):
            self.logger.info("Atualizando Token Navithor...")
            self.comm.updateAuthToken()
            self.last_token_navithor_update = datetime.now()
            self.logger.info("Token Navithor Atualizado!")

    def button_status_monitor(self, device):
        
        previous_status_message = device.status_message

        # Verificar se last_life está mais de 15 segundos atrasado
        if datetime.now() - device.last_life > timedelta(seconds=15):
            device.status_message = "OFFLINE"
            self.db.session.commit()  # Atualiza o banco de dados

            if previous_status_message!=device.status_message:
                self.logger.error(f"Dispositivo {device.ip_device} está OFFLINE.")
        else:
            device.status_message = "ONLINE"
            self.db.session.commit()  

            if previous_status_message!=device.status_message:
                self.logger.info(f"Dispositivo {device.ip_device} está ONLINE.")

        # Verificar se a diferença entre life_sequence e life_previous_sequence é maior que 1 
        if device.life_previous_sequence==None:
            device.life_previous_sequence = 0

        if device.life_sequence==None:
            device.life_sequence = 0

        #logging.warning(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")

        if device.life_sequence - device.life_previous_sequence > 1:
            self.logger.warning(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")



    def checkButtonStatus(self):
        self.logger.debug("Verificando status botoeiras")
        devices = ButtonStatus.query.all()
        for device in devices:
            self.button_status_monitor(device)


    def checkMissionStatus(self):
        self.logger.debug("Verificando status missões")

        # buscamos missoes na API do navithor.
        navithor_missions = self.comm.get_mission_status() 
        
        # buscamos todos as missoes no banco de dados.
        local_missions = Mission.query.filter(Mission.status!='FINALIZADO').all()


        # varremos as missoes em nosso db, e atualizamos com os status do navithor.
        # se a missao do db nao existir no status navithor, assumimos como concluido.
        # se  a missao é concluida em uma posicao gerenciavel por nós, por ex os buffer, liberamos ou ocupamos a posicao.

        # passamos pelas missoes cadastradas em nosso db...
        for l_m in local_missions:        
            existsOnNavithor = False
            
            # passamos pelas missoes cadastradas no navithor...
            for nt_m in navithor_missions:
                navithor_id = nt_m["Id"]
                navithor_state = nt_m["State"] #StateEnum (estado geral da missao)
                local_id = nt_m["ExternalId"]
                agv = nt_m["AssignedMachineId"]
                current_step_index = nt_m["CurrentStepIndex"]
                steps = nt_m["Steps"]

                # passamos pelos passos de cada missao.
                for idx_step in range(len(steps)):
                    nt_s = steps[idx_step]
                    # atualizamos os status de cada passo individualmente.
                    if l_m.id_server == navithor_id and l_m.id_local == local_id and l_m.step_id==idx_step:
                        existsOnNavithor = True
                        if l_m.status != nt_s["StepStatus"]:
                            l_m.status = nt_s["StepStatus"]
                            l_m.dt_updated = datetime.utcnow()
                            self.logger.info(f"Missão atualizada: id_local={local_id}, id_server={navithor_id}")

                            # verifica se a posicao é um target.
                            target_pos = int(nt_s["CurrentTargetId"])
                            if nt_s["StepStatus"]=="Complete":

                                if self.buffers.is_position_buffer(target_pos):
                                    if nt_s["StepType"]=="Pickup":
                                        # retirou. setamos buffer vazio.
                                        self.buffers.set_position_ocupation_by_tag_pos(target_pos, occupied=False)

                                    if nt_s["StepType"]=="Dropoff": 
                                        # colocou. setamos buffer ocupado.
                                        self.buffers.set_position_ocupation_by_tag_pos(target_pos, occupied=False)
                                else:
                                    self.logger.info(f"Passo da missão foi finalizada em na posição {target_pos} que não é buffer.")

            if not existsOnNavithor:
                # seta como concluido.
                self.logger.info(f"Passo da missão {l_m.id_server} (id local:{l_m.id_local}) não existe mais no navithor. Finalizamos.")
                if l_m.status=="Complete":
                    self.logger.error(f"O passo foi finalizado fora de ciclo! Ultimo status: {l_m.status}")

                l_m.status = "FINALIZADO"

                # tambem setamos como finalizado no chamado da botoeira.
                button_call = ButtonCall.query.get(l_m.id_local)

                # Verifique se o registro existe
                if button_call:
                    # Atualize o status da missão para "Concluido"
                    button_call.mission_status = "FINALIZADO"

        self.db.session.commit()
        

