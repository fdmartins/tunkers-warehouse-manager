from threading import Thread
import time
from ..protocols import Navithor
import logging


class MissionControl:
    def __init__(self, db):
        self.logger = logging.getLogger(__name__)

        self.logger.info("iniciando Mission Control...")

        self.db = db

        self.comm = Navithor()

        # inicia thread.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("Mission Control iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            self.run()
            time.sleep(1)


    def run(self):
        
        # verificamos chamados botoeiras.
        #self.logger.debug("verificando status botoeiras")

        # verificamos se tem agv disponivel.
        #self.logger.debug("verificando algum agv disponivel")
        #self.comm.check_agv()

        # montamos a sequencia de missões de cordo com o chamado e a maquina.
        #self.logger.debug("verificando algum agv disponivel")

        # enviamos ao navithor.
        self.logger.info("Enviando Missão...")
        self.comm.send_mission(id=1, missions=[])
