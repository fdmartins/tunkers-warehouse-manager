from ..protocols.defines import StepType
from .steps import STEPS
import logging

class EMBALAGEM_K:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    

        self.machine_positions = {
            1787: {"POS_ENTRADA":1080,"POS_SAIDA":1080  }
        }

    def entrega_palete(self, btn_call):
        
        steps = STEPS()

        # buscamos pallet cheio no buffer
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call.sku, buffers_allowed=[5,6,7, ])
        if tag_load==None:
            self.logger.error(f"Não existe pallet com sku {btn_call.sku} no buffer! ")
            return None

        steps.insert(StepType.Pickup, tag_load)

        # carrega palete cheio na maquina
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA"]
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 


    def retira_palete(self, btn_call):
        
        steps = STEPS()

        # carrega palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA"]
        steps.insert(StepType.Pickup, tag_load)

        sku = "EXPEDICAO"

        # descarreta pallete cheio na expedicao..
        buffers_allowed = [9, ]

        tag_unload, area_id_sku = self.buffers.get_free_pos(sku, buffers_allowed=buffers_allowed)
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel na expedicao!")
            return None
        
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 