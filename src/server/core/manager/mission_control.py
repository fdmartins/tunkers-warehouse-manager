from threading import Thread
import time
from core.models import History
from ..models.mission import Mission
from ..manager.steps_generator import StepsMachineGenerator
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
        
            steps = self.steps_generator.get_steps(btn_call)

            # se o destino eh buffer. Verificamos se ja existe algum STEP de missao para a mesma rua. Se sim, aguardamos a conclusão da missao anterior.
            # varremos steps, verificamos se alguma posicao ja foi enviada ao navithor e ainda esta com status diferente de Completed.
            if steps!=None:
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