from threading import Thread
from ..models.buttons import ButtonStatus
import time
import logging
from datetime import datetime, timedelta
from core import app

class StatusControl:
    def __init__(self, db):
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Iniciando StatusControl...")

        self.db = db

        # inicia thread.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("StatusControl Iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            with app.app_context():
                self.checkButtonStatus()
                self.checkMissionStatus()
                time.sleep(2)


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
        if device.life_sequence - device.life_previous_sequence > 1:
            logging.warning(f"Sequencia de LIFE ATRASADA no dispositivo {device.ip_device}...")



    def checkButtonStatus(self):
        self.logger.debug("Verificando status botoeiras")
        devices = ButtonStatus.query.all()
        for device in devices:
            self.button_status_monitor(device)


    def checkMissionStatus(self):
        self.logger.debug("Verificando status missões")

