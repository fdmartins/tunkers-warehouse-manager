from ..protocols.defines import StepType
from .steps import STEPS
import logging

class RETROFI:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
        self.machine_positions = {
            438: {"POS_CHEIO":240, "POS_VAZIO":250},
            420: {"POS_CHEIO":220, "POS_VAZIO":230},
            419: {"POS_CHEIO":200, "POS_VAZIO":210},
            416: {"POS_CHEIO":180, "POS_VAZIO":190},
            415: {"POS_CHEIO":160, "POS_VAZIO":170},
            422: {"POS_CHEIO":140, "POS_VAZIO":150},
            421: {"POS_CHEIO":120, "POS_VAZIO":130},
            529: {"POS_CHEIO":100, "POS_VAZIO":110},
            528: {"POS_CHEIO":80, "POS_VAZIO":90},
            527: {"POS_CHEIO":6, "POS_VAZIO":70},
            443: {"POS_CHEIO":60, "POS_VAZIO":50},
            439: {"POS_CHEIO":40, "POS_VAZIO":30},
            489: {"POS_CHEIO":20, "POS_VAZIO":10},
            670: {"POS_CHEIO":2, "POS_VAZIO":1},
        }


    
    def abastece_carretel_vazio_retira_carretel_cheio(self, btn_call, actual_steps):
        # CALL1

        steps = STEPS()

        # carrega carretel vazio no buffer.
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, "CARRETEL VAZIO", buffers_allowed=[1, ])

        # descarrega carretel CHEIO no buffer. (id 2)
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, btn_call.sku, buffers_allowed=[2, ])


        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 

        if actual_steps==0:

            if tag_load==None:
                self.logger.error(f"Não temos carretel vazio disponivel! ")
                btn_call.info = f"Sem carretel vazio no buffer"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            if tag_final_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel cheio!")
                btn_call.info = f"Sem espaco livre no buffer de carretel cheio"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None

            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()
        
        
        if actual_steps==1:
                
            steps.insert(StepType.Pickup, tag_load)

            # descarrega carretel vazio na maquina.
            tag_unload = self.machine_positions[btn_call.id_machine]["POS_VAZIO"]
            steps.insert(StepType.Dropoff, tag_unload)

            # carrega carretel cheio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_CHEIO"]
            steps.insert(StepType.Pickup, tag_load)

            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)

            return steps.getSteps()
                
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()
    
    def retira_carretel_cheio(self, btn_call, actual_steps):
        # NOVO - proposta 20241205

        steps = STEPS()

        # descarrega carretel CHEIO no buffer. (id 2)
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call, btn_call.sku, buffers_allowed=[2, ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_unload)
            ]) 

        if actual_steps==0:
            # carrega carretel cheio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_CHEIO"]
            steps.insert(StepType.Pickup, tag_load)

            
            if tag_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel cheio!")
                btn_call.info = f"Sem espaco livre no buffer de carretel cheio"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
        
            
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    

    def retira_carretel_cheio_nao_conforme(self, btn_call, actual_steps):
        # NOVO - proposta 20241205

        steps = STEPS()

        # descarrega carretel CHEIO no buffer. (id 2)
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "CARRETEL N/C", buffers_allowed=[2, ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_unload), 
            ]) 

        if actual_steps==0:
            # carrega carretel cheio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_CHEIO"]
            steps.insert(StepType.Pickup, tag_load)

            
            if tag_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel cheio!")
                btn_call.info = f"Sem espaco livre no buffer de carretel cheio"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
        
            
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    


    def abastece_carretel_vazio_retira_carretel_nao_conforme(self, btn_call, actual_steps):
        # CALL 2

        steps = STEPS()

        # carrega carretel vazio no buffer.
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, "CARRETEL VAZIO", buffers_allowed=[1, ])

        # descarrega carretel NAO CONFORME no buffer. (id 3)
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "CARRETEL N/C", buffers_allowed=[3, ])

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 
        

        if actual_steps==0:

            if tag_load==None:
                self.logger.error(f"Não temos carretel vazio disponivel! ")
                btn_call.info = f"Sem carretel vazio no buffer"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            if tag_final_unload==None:
                self.logger.error(f"Não existe vagas buffer não conforme")
                btn_call.info = f"Sem vaga no buffer NAO CONFORME"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None

            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()


        if actual_steps==1:
                
            steps.insert(StepType.Pickup, tag_load)

            # descarrega carretel vazio na maquina.
            tag_unload = self.machine_positions[btn_call.id_machine]["POS_VAZIO"]
            steps.insert(StepType.Dropoff, tag_unload)

            # carrega carretel cheio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_CHEIO"]
            steps.insert(StepType.Pickup, tag_load)
                
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)

            return steps.getSteps()
        
                
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()
    

    def abastece_carretel_vazio(self, btn_call, actual_steps):

        steps = STEPS()

        # carrega carretel vazio no buffer.
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, "CARRETEL VAZIO", buffers_allowed=[1, ])


        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            None
            ]) 

        if actual_steps==0:

            if tag_load==None:
                self.logger.error(f"Não temos carretel vazio disponivel! ")
                btn_call.info = f"Sem carretel vazio no buffer"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None

            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()


        steps.insert(StepType.Pickup, tag_load)

        # descarrega carretel vazio na maquina.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_VAZIO"]
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()