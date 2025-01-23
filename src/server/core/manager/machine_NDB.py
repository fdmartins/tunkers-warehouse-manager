from ..protocols.defines import StepType
from .steps import STEPS
import logging

class NDB:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
        #[3070,3071,3072,3073,3074,3075]:
        self.machine_positions = {
            3070: {"POS_ENTRADA":2010 },
            3071: {"POS_ENTRADA":2020 },
            3072: {"POS_ENTRADA":2030 },
            3073: {"POS_ENTRADA":2040 },
            3074: {"POS_ENTRADA":2050 },
            3075: {"POS_ENTRADA":2060 }
        }


    def entrega_palete(self, btn_call, actual_steps):
        
        steps = STEPS()

        # carreta palete depositado manualmente por empilhador.
        tag_load = 2000
        steps.insert(StepType.Pickup, tag_load)

        # descarrega na maquina solicitada.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA"]
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 
    

    def retira_palete(self, btn_call, actual_steps):
        
        steps = STEPS()

        # carrega na maquina solicitada.
        tag_load = self.machine_positions[btn_call.id_machine]["POS_ENTRADA"]
        steps.insert(StepType.Pickup, tag_load)

        # descarrega na posicao unica onde empilhador retira.
        tag_unload = 2000
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 

    