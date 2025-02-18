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


    def abastece_carretel_cheio_retira_carretel_vazio(self, btn_call, actual_steps):
        # CALL1

        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios (id 2)
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, btn_call.sku, buffers_allowed=[2, ])

        # descarrega carretel vazio no buffer. (id 1)
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "CARRETEL VAZIO", buffers_allowed=[1, ])

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 

        if actual_steps==0:
            if tag_load==None:
                self.logger.error(f"Não existe carretel com sku {btn_call.sku} no buffer 2! ")
                btn_call.info = f"Sem carretel sku {btn_call.sku} no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            if tag_final_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel vazio!")
                btn_call.info = f"Sem vagas no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()

        if actual_steps==1:
            
            steps.insert(StepType.Pickup, tag_load)

            # descarrega carretel cheio na maquina.
            tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
            steps.insert(StepType.Dropoff, tag_unload)

            # carrega carretel vazio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_VAZIO"]
            steps.insert(StepType.Pickup, tag_load)
            
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)

            return steps.getSteps()

                    
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()

    def abastece_carretel_cheio_nao_conforme_retira_carretel_vazio(self, btn_call, actual_steps):
        # novo - proposta 20241205

        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, "CARRETEL N/C", buffers_allowed=[3, ])

        # descarrega carretel vazio no buffer. (id 1)
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "CARRETEL VAZIO", buffers_allowed=[1, ])

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 

        if actual_steps==0:
            if tag_load==None:
                self.logger.error(f"Não existe carretel com sku CARRETEL N/C no buffer 3! ")
                btn_call.info = f"Sem carretel sku CARRETEL N/C no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            if tag_final_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel vazio!")
                btn_call.info = f"Sem vagas no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()
        
        if actual_steps==1:

            steps.insert(StepType.Pickup, tag_load)

            # descarrega carretel cheio na maquina.
            tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]
            steps.insert(StepType.Dropoff, tag_unload)

            # carrega carretel vazio na maquina.
            tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_VAZIO"]
            steps.insert(StepType.Pickup, tag_load)

            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)

            return steps.getSteps()
        
                    
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()
    
    def so_abastece_carretel_nao_conforme(self, btn_call, actual_steps):
        # novo - proposta 20241205
        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios NC
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, "CARRETEL N/C", buffers_allowed=[3, ])

        # descarrega carretel cheio na maquina.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            None
            ]) 

        if actual_steps==0:   
            if tag_load==None:
                self.logger.error(f"Não existe carretel com sku CARRETEL N/C no buffer 3! ")
                btn_call.info = f"Sem carretel CARRETEL N/C no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
                    
            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()
    
        steps.insert(StepType.Pickup, tag_load)

        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    

    def retira_carretel_nao_conforme(self, btn_call, actual_steps):
        steps = STEPS()

        # carregamos o carretel nao conforme na entrada.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]

        # descarga no carretel nao conforme.
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "CARRETEL N/C", buffers_allowed=[3, ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 


        if actual_steps==0:        
            if tag_final_unload==None:
                self.logger.error(f"Não existe vagas para descarregar carretel  N/C!")
                btn_call.info = f"Sem vagas no buffer carretel N/C! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            steps.insert(StepType.Pickup, tag_load)
        
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
        
        
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()
    
    def retira_carretel_errado(self, btn_call, actual_steps):
        steps = STEPS()

        # carregamos o carretel errado na entrada.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]

        # descarregamos o carretel no buffer com o sku corrigido.
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, btn_call.sku, buffers_allowed=[2, ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 
        
        if actual_steps==0:        
            if tag_final_unload==None:
                self.logger.error(f"Não temos carretel vazio disponivel!")
                btn_call.info = f"Sem carretel vazio no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            steps.insert(StepType.Pickup, tag_load)
        
            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
            
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps()
    
    def so_abastece_carretel(self, btn_call, actual_steps):
        steps = STEPS()

        # buscamos carretel cheio no buffer de cheios (id 2)
        tag_load, area_id_sku = self.buffers.get_occupied_pos_of_sku(btn_call, btn_call.sku, buffers_allowed=[2, ])

        # descarrega carretel cheio na maquina.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA_CHEIO"]

        btn_call.set_reserved_pos([
            self.buffers.get_wait_pos_of(tag_load), 
            None
            ]) 

        if actual_steps==0:   
            if tag_load==None:
                self.logger.error(f"Não existe carretel com sku {btn_call.sku} no buffer 2! ")
                btn_call.info = f"Sem carretel sku {btn_call.sku} no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
                    
            # posicionamos AGV na entrada do buffer
            tag_load = self.buffers.get_wait_pos_of(tag_load)
            steps.insert(StepType.Drive, tag_load, wait_for_extension=True)
            return steps.getSteps()
    
        steps.insert(StepType.Pickup, tag_load)

        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps()
    
    def retira_palete(self, btn_call, actual_steps):
        
        steps = STEPS()

        # carreta palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA_CHEIO"]

        # descarreta pallete cheio no buffer.
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, btn_call.sku, buffers_allowed=[5, 7 ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 

        if actual_steps==0:   
        
            if tag_final_unload==None:
                self.logger.error(f"Não temos posicao livre disponivel no buffer!")
                btn_call.info = f"Sem posicao livre no buffer! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            steps.insert(StepType.Pickup, tag_load)

            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
            

        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps() 

    
    def retira_palete_incompleto(self, btn_call, actual_steps):
        steps = STEPS()

        # carrega palete cheio na maquina
        tag_load = self.machine_positions[btn_call.id_machine]["POS_SAIDA_CHEIO"]

        # descarreta pallete cheio no buffer.
        tag_final_unload, area_id_sku = self.buffers.get_free_pos(btn_call, "PALETE INCOMPLETO", buffers_allowed=[4, ])

        btn_call.set_reserved_pos([
            None,
            self.buffers.get_wait_pos_of(tag_final_unload)
            ]) 

        if actual_steps==0:
            if tag_final_unload==None:
                self.logger.error(f"Não temos posicao livre disponivel no buffer!")
                btn_call.info = f"Sem posicao livre no buffer incompleto! "
                btn_call.mission_status = "FINALIZADO_ERRO"
                return None
            
            steps.insert(StepType.Pickup, tag_load)

            # posicionamos AGV na entrada do buffer
            tag_unload = self.buffers.get_wait_pos_of(tag_final_unload)
            steps.insert(StepType.Drive, tag_unload, wait_for_extension=True)
            return steps.getSteps()
            
        steps.insert(StepType.Dropoff, tag_final_unload)

        return steps.getSteps() 
    
    