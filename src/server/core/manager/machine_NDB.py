from ..protocols.defines import StepType
from .steps import STEPS
import logging

class NDB:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            2010: {"POS_ENTRADA":2010 },
            2020: {"POS_ENTRADA":2020 },
            2030: {"POS_ENTRADA":2030 },
            2040: {"POS_ENTRADA":2040 },
            2050: {"POS_ENTRADA":2050 },
            2060: {"POS_ENTRADA":2060 }
        }


    def entrega_palete(self, btn_call):
        
        steps = STEPS()

        # carreta palete depositado manualmente por empilhador.
        tag_load = 2000
        steps.insert(StepType.Pickup, tag_load)

        # descarrega na maquina solicitada.
        tag_unload = self.machine_positions[btn_call.id_machine]["POS_ENTRADA"]
        steps.insert(StepType.Dropoff, tag_unload)

        return steps.getSteps() 

    