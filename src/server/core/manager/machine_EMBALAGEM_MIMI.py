from ..protocols.defines import StepType
from .steps import STEPS
import logging

class EMBALAGEM_MIMI:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            2017: {"POS_ENTRADA":1040,"POS_SAIDA":1060  }
        }

    def entrega_palete(self, btn_call, actual_steps):
        
        steps = STEPS()

        # buscamos pallet cheio no buffer
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, btn_call.sku, buffers_allowed=[5,7, ])

        # carrega palete cheio na maquina
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA"]

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            ]) 
        
        if actual_steps==0:
            if tag_load==None:
                self.logger.error(f"Não existe pallet com sku {btn_call.sku} no buffer! ")
                btn_call.info = f"Sem sku {btn_call.sku} no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()
        

        steps.insert(StepType.Pickup, tag_load)

        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 


    def retira_palete(self, btn_call, actual_steps):
        
        steps = STEPS()

        # carrega palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA"]

        # descarreta pallete cheio na expedicao..
        buffers_allowed = [9, ]

        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "EXPEDICAO", buffers_allowed=buffers_allowed)

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            self.buffers.get_wait_pos_of(tag_unload)
            ]) 

        if actual_steps==0:
            if tag_unload==None:
                self.logger.error(f"Não temos posicao livre disponivel na expedicao!")
                btn_call.info = f"Sem espaco na expedicao"
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            steps.insert(StepType.Pickup, tag_load)

            tag_unload = self.buffers.get_wait_pos_of(tag_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
            

        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 