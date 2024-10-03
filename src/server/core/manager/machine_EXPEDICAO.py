from ..protocols.defines import StepType
from .steps import STEPS
import logging

class EXPEDICAO:
    def __init__(self, db, buffers):
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.buffers = buffers
        
    