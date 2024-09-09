import logging
import requests

from .defines import StepType

class Navithor:
    def __init__(self, ip="127.0.0.1", port=123):
        self.logger = logging.getLogger(__name__)

        self.ip = ip
        self.port = port

        self.logger.info("Iniciado Protocolo API Navithor IP {ip} porta {port}")

    def call_api(self, endpoint, payload):
        headers = {
            "Content-Type": "application/json"
        }

        # Faz a requisição POST para a API
        response = requests.post(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)

        # Verifica se a resposta foi bem-sucedida
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro na requisição: {response.status_code}"}
        

    def send_mission(self, id, missions):
        self.logger.info("Enviando Missão ao Navithor...")
        
        endpoint = "/api/missioncreate"

        steps = [  # passos de execucao da missao.
                {
                    "StepType": StepType.Pickup.value, # acao de carga Enum StepType
                    "Options": {
                        "Load": {
                            "RequiredLoadStatus": "LoadAtLocation",
                            "RequiredLoadType": 2
                        },
                        "SortingRules": ["Priority", "Closest"]
                    },
                    "AllowedTargets": [  # carrega qualquer uma das posicoes 1,2,3 priorizando prioridade e proximidade.
                        {"Id": 1},
                    ],
                    "AllowedWaits": [ # se os targets estiverem ocupados/reservados, pode aguardar na posicao 16.
                        {"Id": 16}
                    ]
                },
                {
                    "StepType": "Dropoff", #acao de descarga.
                    "Options": {
                        "Load": {
                            "RequiredLoadType": 2,
                            "RequiredLoadStatus": "LocationHasRoom"
                        }
                    },
                    "AllowedTargets": [  # local que pode descarregar.
                        {"Id": 7}
                    ]
                },
                {
                    "StepType": "Drive",  # acao de apenas se movimentar.
                    "Options": {
                        "WaitForExtension": True
                    },
                    "AllowedTargets": [
                        {"Id": 12}  # estaciona em 12 e aguarda missoes futuras.
                    ]
                }
            ]

        self.logger.info(steps)
        exit()

        payload = {
            "ExternalId": f"Tunkers_{id}",
            "Name": "Gerenciador Tunkers",
            "Options": {
                "Priority": 5
            },
            "Steps": steps
        }

        return self.call_api(endpoint, payload)

 
    def get_mission_status(self, external_id=None, internal_id=None):
        self.logger.debug("Verificando Status das Missões...")

        endpoint = "/api/MissionStatusRequest"
        
        # Define o payload com base no ID disponível
        payload = {}
        if external_id:
            payload["ExternalId"] = external_id
        elif internal_id:
            payload["InternalId"] = internal_id
        else:
            raise ValueError("Você deve fornecer um ExternalId ou um InternalId.")

        return self.call_api(endpoint, payload)


    def extend_mission(self, external_id=None, steps=None):
        url = "/api/MissionExtend"
        
        if not steps or not isinstance(steps, list):
            raise ValueError("Você deve fornecer uma lista de etapas para a missão.")

        # Define o payload
        payload = {
            "Steps": steps
        }
        
        if external_id:
            payload["ExternalId"] = external_id

        return self.call_api(url, payload)


