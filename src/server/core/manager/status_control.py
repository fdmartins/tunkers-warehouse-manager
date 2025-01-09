from threading import Thread

from ..models.mission import Mission
from core.models import History
from ..protocols.navithor import Navithor
from ..models.buttons import ButtonCall, ButtonStatus
import time
import logging
from datetime import datetime, timedelta
from core import app
import json
import traceback

class StatusControl:
    def __init__(self, db, buffers, comm):
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Iniciando StatusControl...")

        self.system_start_date = datetime.now()

        self.db = db
        self.buffers = buffers
        self.comm = comm

        self.last_token_navithor_update = None
        self.last_db_clean = None

        # inicia thread.
        flask_thread = Thread(target=self.run_loop)
        flask_thread.daemon = True
        flask_thread.start()

        self.logger.info("StatusControl Iniciado!")

    def run_loop(self):
        time.sleep(1)
        while True:
            with app.app_context():
                try:
                    self.cleanDB()
                    self.checkButtonStatus()

                    self.mirrorBufferPositionsToNavithor()
                    self.checkAuthTokenNavithor()
                    
                    self.checkMissionStatus()

                    time.sleep(2)
                except Exception as e:
                    self.logger.error(f"ERRO GERAL: {e}")
                    self.logger.error(traceback.format_exc())
                    History.error("SISTEMA", f"{e}")
                    time.sleep(15)


    def cleanDB(self):
        # limpamos dados antigos do banco.
        
        if self.last_db_clean==None or (datetime.now() - self.last_db_clean) > timedelta(hours=24):
            self.logger.info("Removendo dados antigos do Banco de Dados...")

            one_day_ago = datetime.now() - timedelta(days=1)
            three_days_ago = datetime.now() - timedelta(days=3)
            five_days_ago = datetime.now() - timedelta(days=5)
            month_ago = datetime.now() - timedelta(days=30)

            # chamados botoeiras.
            records_to_delete = ButtonCall.query.filter(ButtonCall.dt_creation < five_days_ago).all()
            for record in records_to_delete:
                self.db.session.delete(record)

            # historico
            records_to_delete = History.query.filter(History.level=="ERRO" , History.dt_created < one_day_ago).all()
            for record in records_to_delete:
                self.db.session.delete(record)

            records_to_delete = History.query.filter(History.level!="ERRO", History.dt_created < month_ago).all()
            for record in records_to_delete:
                self.db.session.delete(record)

            # missoes (steps)
            #print(one_day_ago)
            records_to_delete = Mission.query.filter(Mission.dt_created < five_days_ago).all()
            for record in records_to_delete:
                #print(record)
                self.db.session.delete(record)

            # Commit para aplicar as mudanças no banco de dados
            self.db.session.commit()

            self.last_db_clean = datetime.now()

    def checkAuthTokenNavithor(self):
        # o token tem tempo de validade.
        # renovamos a cada 1 minuto ou quando necessario.
        if self.comm.needAuthToken() or (self.last_token_navithor_update==None) or (datetime.now() - self.last_token_navithor_update) > timedelta(minutes=1):
            #self.logger.info("Atualizando Token Navithor...")
            self.comm.updateAuthToken()
            self.last_token_navithor_update = datetime.now()
            #self.logger.info("Token Navithor Atualizado!")

    def button_status_monitor(self, device):
        
        if datetime.now() - self.system_start_date < timedelta(seconds=15):
            # aguarda 15 segundos antes de iniciar a verificacao, para dar tempo das botoeiras enviarem pelo menos um life.
            # assim nao logamos erroneamente que as botoeiras ficaram offline.
            return
 
        previous_status_message = device.status_message

        # Verificar se last_life está mais de 15 segundos atrasado
        if datetime.now() - device.last_life > timedelta(seconds=15):
            device.status_message = "OFFLINE"
            self.db.session.commit()  # Atualiza o banco de dados

            if previous_status_message!=device.status_message:
                History.error("BOTOEIRA", f"Botoeira {device.ip_device} está OFFLINE - Desligada? WIFI OK?")
                self.logger.error(f"Botoeira {device.ip_device} está OFFLINE.")
        else:
            device.status_message = "ONLINE"
            self.db.session.commit()  

            if previous_status_message!=device.status_message:
                History.info("BOTOEIRA", f"Botoeira {device.ip_device} voltou comunicar")
                self.logger.info(f"Dispositivo {device.ip_device} está ONLINE.")

        # Verificar se a diferença entre life_sequence e life_previous_sequence é maior que 1 
        if device.life_previous_sequence==None:
            device.life_previous_sequence = 0

        if device.life_sequence==None:
            device.life_sequence = 0

        #logging.warning(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")

        if device.life_sequence - device.life_previous_sequence > 1:
            if device.status_message == "ONLINE":
                History.error("BOTOEIRA", f"Sequencia LIFE ATRASADA {device.ip_device} - Reiniciada ou WIFI INSTÁVEL? ")
                self.logger.error(f"Sequencia de LIFE ATRASADA {device.life_previous_sequence} {device.life_sequence} no dispositivo {device.ip_device}...")



    def checkButtonStatus(self):
        self.logger.debug("Verificando status botoeiras")
        devices = ButtonStatus.query.all()
        for device in devices:
            self.button_status_monitor(device)


    # Função que converte automaticamente datetime para uma string
    def datetime_converter(self, o):
        if isinstance(o, datetime):
            return o.isoformat()  # Converte para string no formato ISO
        
    def mirrorBufferPositionsToNavithor(self):
        # atualizamos no navithor os status de ocupacoes das posicoes do buffer.
        positions = self.buffers.get_all_positions_and_ocupations()

        for p in positions:
            navithor_pos = self.comm.get_position_occupation(p["pos"])
            local_pos = p["occupied"]
            if navithor_pos!=local_pos:
                self.logger.warning(f"Posicao {p['pos']} navithor {navithor_pos} local {local_pos}. Corrigido.")
                self.comm.set_position_occupation(p["pos"], p["occupied"])
        
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
            last_step_is_extend_mission = False
            navithor_main_state = "?"
            current_step_index=-1
            steps = []

            # passamos pelas missoes cadastradas no navithor...
            for nt_m in navithor_missions:
    
                local_id = -1
                try:
                    # missoes criadas diretamente no navithor tem id como string.
                    local_id = int(nt_m["ExternalId"])
                except:
                    pass

                # verifica se é o que estamos analisando.
                if local_id != l_m.id_local:
                    continue
                
                navithor_id = nt_m["Id"]
                navithor_main_state = nt_m["State"] #StateEnum (estado geral da missao)
                agv = nt_m["AssignedMachineId"]
                current_step_index = nt_m["CurrentStepIndex"]
                steps = nt_m["Steps"]

                if l_m.mission_status!=navithor_main_state:
                    self.logger.info(f"id({local_id}) Status Missão mudou de {l_m.mission_status} para {navithor_main_state}")

                l_m.mission_status = navithor_main_state

                # passamos pelos passos de cada missao.
                for idx_step in range(len(steps)):
                    nt_s = steps[idx_step]
                    # atualizamos os status de cada passo individualmente.
                    if l_m.id_server == navithor_id and l_m.id_local == local_id and l_m.step_id==idx_step:

                        existsOnNavithor = True
                        last_step_is_extend_mission = l_m.is_extended

                        if l_m.status != nt_s["StepStatus"]:
                            self.logger.info(f"id({local_id}) Step atualizado: id_local={local_id}, id_server={navithor_id} passo {idx_step} posicao {nt_s['CurrentTargetId']} status {l_m.status} => {nt_s['StepStatus']}")
                            self.logger.info(f"id({local_id}) passo atual {idx_step} tem missao extendida? {l_m.is_extended}")
                            # atualizamos as ocupacoes das posicoes no navithor de acordo com as movimentacoes atuais.
                            # isso tem mais um papel de auto correcao em caso de erro de box ocupado no navithor.
                            if nt_s["StepStatus"]=="DrivingToPickup" or nt_s["StepStatus"]=="WaitingForLoad":
                                # entao a posicao de destino deve estar marcada como OCUPADA.
                                if self.comm.get_position_occupation(l_m.position_target)==False:
                                    self.logger.warning(f"id({local_id}) Posicao {l_m.position_target} nao tinha ocupacao no navithor. Marcamos como ocupada para poder efetuar a carga.")
                                    self.comm.set_position_occupation(l_m.position_target, occupied=True)


                            if nt_s["StepStatus"]=="DrivingToDropoff":
                                # entao a posicao de destino deve estar marcada como LIVRE.
                                if self.comm.get_position_occupation(l_m.position_target)==True:
                                    self.logger.warning(f"id({local_id}) Posicao {l_m.position_target} esta como ocupada no navithor. Liberamos para poder efetuar a carga.")
                                    self.comm.set_position_occupation(l_m.position_target, occupied=False)


                                # verificamos necessidade de setar o sku no buffer.
                                # verifica se agv a caminho para descaregar no buffer.
                                if self.buffers.is_position_buffer(l_m.position_target):

                                    # verificamos qual sku é desta missao.
                                    actual_call = ButtonCall.query.get(l_m.id_local)
                                    sku = None
                                    if actual_call!=None:
                                        sku = actual_call.sku

                                        # verifica se a rua ja tem o sku certo.
                                        buffer_id, row_id = self.buffers.find_area_and_row_of_position(l_m.position_target)

                                        sku_in_buffer = self.buffers.get_sku_from_row(buffer_id, row_id)

                                        if self.buffers.is_row_with_sku_editable(buffer_id, row_id):
                                            if sku!=sku_in_buffer:
                                                self.logger.info(f"id({local_id}) SETANDO SKU DO BUFFER DE {sku_in_buffer} para {sku}")
                                                if sku_in_buffer!=None:
                                                    self.logger.error(f"id({local_id}) INESPERADO!! SKU DO BUFFER MUDOU DE {sku_in_buffer} para {sku}")

                                                self.buffers.set_sku_to_row(buffer_id, row_id, sku)

                            # atualizamos o status no banco.
                            l_m.status = nt_s["StepStatus"]
                            l_m.agv = agv
                            l_m.dt_updated = datetime.now()

                            if navithor_main_state=="WaitingExtension" and l_m.status!="Complete":
                                l_m.info = "Navithor aguardando comando para entrar no buffer (WaitingExtension)"

                            
                            # verifica se finalizou em posicao de buffer.
                            # nao nos preocupamos em setar no navithor, pois quando agv descarrega ele ja seta como ocupado.
                            target_pos = int(nt_s["CurrentTargetId"])
                            if nt_s["StepStatus"]=="Complete":

                                l_m.info = ""

                                if self.buffers.is_position_buffer(l_m.position_target):

                                    if nt_s["StepType"]=="Pickup":
                                        # retirou. setamos buffer vazio.
                                        self.buffers.set_position_ocupation_by_tag_pos(target_pos,  occupied=False)

                                        # auto limpeza do sku com rua...
                                        self.logger.info(f"id({local_id}) Verificando necessidade de liberação da rua para novo sku...")
                                        self.buffers.clear_sku_row_with_no_occupation()

                                    if nt_s["StepType"]=="Dropoff": 
                                        # colocou. setamos buffer ocupado.
                                        self.buffers.set_position_ocupation_by_tag_pos(target_pos, occupied=True)

                                        
                                else:
                                    self.logger.info(f"id({local_id}) Passo da missão foi finalizada em na posição {target_pos} que não é buffer.")
                
                #<fim loop steps navithor> 

            #<fim loop missoes navithor> 

            # SO PODEMOS CONSIDERAR COMO FINALIZADO QUANDO O NAVITHOR REMOVE A MISSAO.
            # O STATUS DA MISSAO VAI PARA COMPLETED CADA VEZ QUE TERMINA UM PASSO. NAO PODEMOS USA-LO CONSISTENTEMENTE!!!!
            if not existsOnNavithor:
                                
                if l_m.mission_status!="Completed":

                    self.logger.error(f"id({l_m.id_local}) Missão concluida inesperadamente Ultimo status conhecido: {l_m.mission_status}")
                    l_m.info = f"Missão concluida inesperadamente - Ultimo status conhecido: {l_m.mission_status}"

                l_m.status = "FINALIZADO"

                # Garantimos que todos os passos desta missao foram finalizados.
                #this_steps = Mission.query.filter(Mission.id_local==l_m.id_local).all()
                #for s in this_steps:
                #    s.status = "FINALIZADO"

                # tambem setamos como finalizado no chamado da botoeira.
                button_call = ButtonCall.query.get(l_m.id_local)

                # Verifique se o registro existe
                if button_call:
                    # Atualize o status da missão para "Concluido"
                    button_call.mission_status = "FINALIZADO"
                    button_call.info =  l_m.info
                    
                #self.logger.info(f"Status chamado após: {button_call}")

        self.db.session.commit()
        

