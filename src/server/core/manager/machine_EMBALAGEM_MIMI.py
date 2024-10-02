from ..protocols.defines import StepType
from .steps import STEPS
import logging

class EMBALAGEM_MIMI:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    
        self.machine_positions = {
            6146: {"POS_ENTRADA_CHEIO":460, "POS_ENTRADA_VAZIO":450, "POS_SAIDA_CHEIO":340  },
            6155: {"POS_ENTRADA_CHEIO":440, "POS_ENTRADA_VAZIO":430, "POS_SAIDA_CHEIO":330  },
        }
