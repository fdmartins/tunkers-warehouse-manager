from threading import Thread

from ..models.mission import Mission

from ..protocols.navithor import Navithor
from ..models.buttons import ButtonCall, ButtonStatus
import time
import logging
from datetime import datetime, timedelta
from core import app

class StatusControl:
    def __init__(self, db):
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Iniciando StatusControl...")

        self.db = db

        self.comm = Navithor()

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
                    self.checkButtonStatus()
                    self.checkMissionStatus()
                    time.sleep(2)
            except Exception as e:
                self.logger.error(f"ERRO GERAL: {e}")
                time.sleep(10)


    def button_status_monitor(self, device):
        
        previous_status_message = device.status_message

        # Verificar se last_life está mais de 15 segundos atrasado
        if datetime.now() - device.last_life > timedelta(seconds=15):
            device.status_message = "OFFLINE"
            self.db.session.commit()  # Atualiza o banco de dados

            if previous_status_message!=device.status_message:
                logging.error(f"Dispositivo {device.ip_device} está OFFLINE.")
        else:
            device.status_message = "ONLINE"
            self.db.session.commit()  

            if previous_status_message!=device.status_message:
                logging.info(f"Dispositivo {device.ip_device} está ONLINE.")

        # Verificar se a diferença entre life_sequence e life_previous_sequence é maior que 1 
        if device.life_previous_sequence==None:
            device.life_previous_sequence = 0

        if device.life_sequence==None:
            device.life_sequence = 0

        #logging.warning(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")

        if device.life_sequence - device.life_previous_sequence > 1:
            logging.warning(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")



    def checkButtonStatus(self):
        self.logger.debug("Verificando status botoeiras")
        devices = ButtonStatus.query.all()
        for device in devices:
            self.button_status_monitor(device)


    def checkMissionStatus(self):
        self.logger.debug("Verificando status missões")
        
        # buscamos todos as missoes com o status diferentes de completed.
        button_calls = ButtonCall.query.filter(ButtonCall.mission_status!='FINALIZADO').all()

        # consultamos e atualizamos os status das missoes diferentes de completes.
        for b in button_calls:        
            id_local = b.id
            id_server = b.id_navithor
            
            actual_state = self.comm.get_mission_status(external_id=id_local, internal_id=id_server)

            # inserimos ou atualizamos se existir o mesmo id_local e id_server
            # Verificar se a missão já existe com o mesmo id_local e id_server
            mission = Mission.query.filter_by(id_local=id_local, id_server=id_server).first()

            if mission:
                # Atualizar campos se a missão existir
                mission.status = actual_state.status
                mission.current_step_type = actual_state.current_step_type
                mission.dt_updated = datetime.utcnow()
                self.logger.info(f"Missão atualizada: id_local={id_local}, id_server={id_server}")
            else:
                # Criar nova missão se não existir
                mission = Mission(
                    id_local=id_local,
                    id_server=id_server,
                    status=actual_state.status,
                    current_step_type=actual_state.current_step_type,
                    dt_created=datetime.utcnow(),
                    dt_updated=datetime.utcnow()
                )
                self.db.session.add(mission)
                self.logger.info(f"Nova missão criada para monitoramento: id_local={id_local}, id_server={id_server}")
            
            # Confirmar alterações no banco de dados
            self.db.session.commit()
        

