from ..protocols.defines import StepType
import logging

class STEPS:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steps = []

    def insert(self, step_type:StepType, target_pos, wait_for_extension=False):

        self.logger.info(f"Adicionado Step {step_type.value} pos {target_pos} = wait_extension {wait_for_extension}")

        self.steps.append(  
            {
                "StepType": step_type.value, # acao de carga Enum StepType
                "Options": {
                    #"Load": {
                    #    "RequiredLoadStatus": "LoadAtLocation",
                    #    "RequiredLoadType": 2
                    #},
                    "SortingRules": ["Priority", "Closest"],
                    "WaitForExtension": wait_for_extension
                },
                "AllowedTargets": [  # vai para qualquer uma dessas posicoes, priorizando prioridade e proximidade.
                    {"Id": target_pos},
                ],
                "AllowedWaits": [ # se os targets estiverem ocupados/reservados, pode aguardar nessas posicoes..
                    # {"Id": 16}
                ]
            }
        )

    def getSteps(self):
        return self.steps
        

    
