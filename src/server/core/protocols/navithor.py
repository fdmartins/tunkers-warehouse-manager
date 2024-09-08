import logging

class Navithor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Usando Protocolo API Navithor")

    def send_mission(self):
        self.logger.info("Enviando Missão ao Navithor...")
        pass

    def check_status(self):
        self.logger.debug("Verificando Status das Missões...")
        pass

    def check_agv(self):
        self.logger.debug("Verificando Status AGVs...")
        pass