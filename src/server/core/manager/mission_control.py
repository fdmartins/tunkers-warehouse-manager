from threading import Thread
import time

from ..models.buttons import ButtonCall
from ..protocols import Navithor
import logging
from core import app

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
            try:
                with app.app_context():
                    self.run()
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"ERRO GERAL: {e}")
                time.sleep(10)

            


    def run(self):
        
        # verificamos chamados botoeiras.
        self.logger.debug("verificando chamados das botoeiras")

        button_calls = ButtonCall.query.filter(ButtonCall.mission_status!='FINALIZADO').all()

        for bc in button_calls:
        
            id_chamado = bc.id

            # montamos a sequencia de missões de cordo com o chamado e a maquina.
            missions = []
            # TODO.....
            # TODO....

            # enviamos ao navithor.
            self.logger.info(f"Enviando Missão ID {id_chamado}...")
            status_response = self.comm.send_mission(id_local=id_chamado, missions=missions)

            if status_response.success == False:
                self.logger.error(f"Erro ao criar missão no navithor. {status_response}")
            else:
                self.logger.info(f"Status Missão {status_response} ")

            # armazenamos no chamado, o id do servidor - ele é usado para monitorar o status das missoes.
            id_server = status_response.InternalId

            bc.id_navithor = id_server

        self.db.session.commit()