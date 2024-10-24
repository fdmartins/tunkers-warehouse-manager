from ..protocols.defines import StepType
from .steps import STEPS
import logging

class CAPACAPA:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        


        self.machine_positions = {
            6150: {"POS_ENTRADA_CHEIO":670, "POS_ENTRADA_VAZIO":660, "POS_SAIDA_CHEIO":960  },
            6171: {"POS_ENTRADA_CHEIO":650, "POS_ENTRADA_VAZIO":640, "POS_SAIDA_CHEIO":940  },
            6170: {"POS_ENTRADA_CHEIO":630, "POS_ENTRADA_VAZIO":620, "POS_SAIDA_CHEIO":920  },
            6164: {"POS_ENTRADA_CHEIO":610, "POS_ENTRADA_VAZIO":600, "POS_SAIDA_CHEIO":900  },
            6162: {"POS_ENTRADA_CHEIO":590, "POS_ENTRADA_VAZIO":580, "POS_SAIDA_CHEIO":880  },
            6161: {"POS_ENTRADA_CHEIO":570, "POS_ENTRADA_VAZIO":560, "POS_SAIDA_CHEIO":860  },
            6159: {"POS_ENTRADA_CHEIO":550, "POS_ENTRADA_VAZIO":540, "POS_SAIDA_CHEIO":840  },
            6158: {"POS_ENTRADA_CHEIO":530, "POS_ENTRADA_VAZIO":520, "POS_SAIDA_CHEIO":820  },
            6157: {"POS_ENTRADA_CHEIO":510, "POS_ENTRADA_VAZIO":500, "POS_SAIDA_CHEIO":800  },
        }



    def abastece_carretel_cheio_retira_carretel_vazio(self, btn_call):
        # CALL1

        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios (id 2)
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call.sku, buffers_allowed=[2, ])
        if tag_load==None:
            self.logger.error(f"Não existe carretel com sku {btn_call.sku} no buffer 2! ")
            btn_call.info = f"Sem carretel sku {btn_call.sku} no buffer! "
            btn_call.mission_status = "FINALIZADO_ERRO"
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
            btn_call.info = f"Sem espaco no buffer para carretel vazio"
            #btn_call.mission_status = "FINALIZADO_ERRO"
            return None
            
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()

    
    def retira_carretel_nao_conforme(self, btn_call):
        steps = STEPS()

        # carregamos o carretel nao conforme na entrada.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
        steps.insert(StepType.Dropoff, tag_load)

        tag_unload, area_id_sku = self.buffers.get_free_pos("CARRETEL N/C", buffers_allowed=[3, ])
        if tag_unload==None:
            self.logger.error(f"Não existe vagas para descarregar carretel NC!")
            btn_call.info = f"Sem espaco no buffer para carretel N/C"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None
            
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    
    def retira_carretel_errado(self, btn_call):
        steps = STEPS()

        # carregamos o carretel errado na entrada.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
        steps.insert(StepType.Dropoff, tag_load)

        # descarregamos o carretel no buffer com o sku corrigido.
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call.sku, buffers_allowed=[2, ])
        if tag_unload==None:
            self.logger.error(f"Não temos carretel vazio disponivel!")
            btn_call.info = f"Sem carretel vazio no buffer"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None
        
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    
    def so_abastece_carretel(self, btn_call):
        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios (id 2)
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call.sku, buffers_allowed=[2, ])
        if tag_load==None:
            self.logger.error(f"Não existe carretel com sku {btn_call.sku} no buffer 2! ")
            btn_call.info = f"Sem carretel sku {btn_call.sku} no buffer! "
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None

        steps.insert(StepType.Pickup, tag_load)

        # descarrega carretel cheio na maquina.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
        steps.insert(StepType.Dropoff, tag_unload)


        return steps.getSteps()
    
    def retira_palete(self, btn_call):
        
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA_CHEIO"]
        steps.insert(StepType.Pickup, tag_load)

        # descarreta pallete cheio no buffer.
        tag_unload, area_id_sku = self.buffers.get_free_pos(btn_call.sku, buffers_allowed=[6, 7, ])
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel no buffer!")
            btn_call.info = f"Sem posicao no buffer de pallet"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None

        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 

    
    def retira_palete_incompleto(self, btn_call):
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA_CHEIO"]
        steps.insert(StepType.Pickup, tag_load)

        # descarreta pallete cheio no buffer.
        tag_unload, area_id_sku = self.buffers.get_free_pos("PALETE INCOMPLETO", buffers_allowed=[4, ])
        if tag_unload==None:
            self.logger.error(f"Não temos posicao livre disponivel no buffer!")
            btn_call.info = f"Sem posicao no buffer de pallet incompleto"
            btn_call.mission_status = "FINALIZADO_ERRO"
            return None
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 
