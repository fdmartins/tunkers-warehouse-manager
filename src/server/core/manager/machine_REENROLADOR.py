from ..protocols.defines import StepType
from .steps import STEPS
import logging

class REENROLADOR:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            6066: {"POS_SAIDA":760 },
            6067: {"POS_SAIDA":780 }
        }


    def retira_palete(self, btn_call):
        
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA"]
        steps.insert(StepType.Pickup, tag_load)

        # descarrega pallete cheio no buffer. 
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call.sku, buffers_allowed=[5, ])
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel no buffer!")
            btn_call.info = f"Sem espaco no buffer"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 

    
    def retira_palete_incompleto(self, btn_call):
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA"]
        steps.insert(StepType.Pickup, tag_load)

        # descarreta pallete cheio no buffer.
        tag_unload, area_id_sku = self.buffers.get_free_pos("PALETE INCOMPLETO", buffers_allowed=[4, ])
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel no buffer!")
            btn_call.info = f"Sem espaco livre buffer de incompletos"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 