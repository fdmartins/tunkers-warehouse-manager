from ..protocols.defines import StepType
from .steps import STEPS
import logging

class SAMPS:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            6146: {"POS_ENTRADA_CHEIO":460, "POS_ENTRADA_VAZIO":450, "POS_SAIDA_CHEIO":340  },
            6155: {"POS_ENTRADA_CHEIO":440, "POS_ENTRADA_VAZIO":430, "POS_SAIDA_CHEIO":330  },
            6148: {"POS_ENTRADA_CHEIO":420, "POS_ENTRADA_VAZIO":410, "POS_SAIDA_CHEIO":320  },
            6151: {"POS_ENTRADA_CHEIO":400, "POS_ENTRADA_VAZIO":390, "POS_SAIDA_CHEIO":310  },
            6144: {"POS_ENTRADA_CHEIO":360, "POS_ENTRADA_VAZIO":370, "POS_SAIDA_CHEIO":300  },
        }


    def abastece_carretel_cheio_retira_carretel_vazio(self, btn_call):
        # CALL1

        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios (id 2)
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call.sku, buffers_allowed=[2, ])
        if tag_load==None:
            self.logger.error(f"Não existe carretel com sku {btn_call.sku} no buffer 2! ")
            return None

        steps.insert(StepType.Pickup, tag_load)

        # descarrega carretel cheio na maquina.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
        steps.insert(StepType.Dropoff, tag_unload)

        # carrega carretel vazio na maquina.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_VAZIO"]
        steps.insert(StepType.Pickup, tag_load)

        # descarrega carretel vazio no buffer. (id 1)
        tag_unload, area_id_sku = self.buffers.get_free_pos("CARRETEL VAZIO", buffers_allowed=[1, ])
        if tag_unload==None:
            self.logger.error(f"Não existe vagas para descarregar carretel vazio!")
            return None
            
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()

    
    def retira_carretel_nao_conforme(self, btn_call):
        steps = STEPS()
        return steps.getSteps()
    
    def retira_carretel_errado(self, btn_call):
        steps = STEPS()
        return steps.getSteps()
    
    def so_abastece_carretel(self, btn_call):
        steps = STEPS()
        return steps.getSteps()
    
    def retira_palete(self, btn_call):
        
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA_CHEIO"]
        steps.insert(StepType.Pickup, tag_load)

        # descarreta pallete cheio no buffer.
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call.sku, buffers_allowed=[5, ])
        if tag_unload==None:
            self.logger.error(f"Não temos carretel vazio disponivel!")
            return None
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 

    
    def retira_palete_incompleto(self, btn_call):
        steps = STEPS()
        return steps.getSteps()
    
    def abastece_palete_incompleto(self, btn_call):
        steps = STEPS()
        return steps.getSteps()
    