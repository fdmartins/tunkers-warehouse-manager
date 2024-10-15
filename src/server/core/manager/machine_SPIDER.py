from ..protocols.defines import StepType
from .steps import STEPS
import logging

class SPIDER:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            2015: {"POS_SAIDA":740 }
        }


    def retira_palete(self, btn_call):
        
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA"]
        steps.insert(StepType.Pickup, tag_load)

        # descarreta pallete cheio no buffer.
        buffers_allowed = [6,7 ]
        if btn_call.sku in ["40479815"]:
             buffers_allowed = [8, ] # regiao L

        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call.sku, buffers_allowed=buffers_allowed)
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel no buffer!")
            btn_call.info = f"Sem espaco livre no buffer"
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
            btn_call.info = f"Sem espaco livre no buffer incompletos"
            return None
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 