import logging
import requests

from .defines import StepType

class Navithor:
    def __init__(self, ip="127.0.0.1", port=1234):
        self.logger = logging.getLogger(__name__)

        self.ip = ip
        self.port = port

        self.logger.info(f"Iniciado Protocolo API Navithor IP {ip} porta {port}")

        self.access_token = None

        try:
            self.updateAuthToken()
        except Exception as err:
            self.logger.error("Falha atualizacao token autenticacao navithor: " + str(err))

    def call_api(self, endpoint, payload={}, method="POST", headers=None):

        if headers==None:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                "Content-Type": "application/json"
            }

        # Faz a requisição POST para a API
        if method=="POST":
            response = requests.post(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)
        else:
            response = requests.get(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)


        return response.json()
    
        # Verifica se a resposta foi bem-sucedida
        #if response.status_code == 200:
        #    return response.json()
        #else:
        #    return {"error": f"Erro na requisição: {response.status_code}"}
        
    def checkVersion(self):
        endpoint = "/api/getVersion"
 
        return self.call_api(endpoint)


    def updateAuthToken(self):
        return
        endpoint = "/api/token"

        payload = 'username=navitec&password=navitrol&grant_type=password'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self.call_api(endpoint, payload, headers)

        self.access_token = response["access_token"]

        response = self.checkVersion()    

        self.logger.info(f"Versão Navithor: {response} ")


    def send_mission(self, id_local, steps):
        self.logger.info("Enviando Missão ao Navithor...")
        return id_local
        
        endpoint = "/api/missioncreate"

        payload = {
            "ExternalId": id_local,
            "Name": "Gerenciador Tunkers",
            "Options": {
                "Priority": 3
            },
            "Steps": steps
        }

        self.logger.info(payload)
        #exit()

        response =  self.call_api(endpoint, payload)

        if response["Success"]==False:
            self.logger.error(f"Falha ao criar missão id {id_local}: {response}")
            raise Exception(f"Falha ao criar missão id {id_local}: {response['Description']}") 
        
        return response["InternalId"]

 
    def get_mission_status(self, external_id):
        #self.logger.debug("Verificando Status das Missões...")

        #endpoint = "/api/MissionStatusRequest"
        endpoint = "/api/GetMissions" # retorna mais ifnormacoes uteis, como o passo que esta sendo executado!!)
        
        response = self.call_api(endpoint)

        for m in response:
            if m["ExternalId"]==external_id:
                return m
            
        return None


    def extend_mission(self, external_id=None, steps=None):
        self.logger.info("Enviando Extensão da Missão ao Navithor...")
        return external_id
    
        endpoint = "/api/MissionExtend"

        # Define o payload
        payload = {
            "ExternalId": external_id,
            "Steps": steps
        }

        response =  self.call_api(endpoint, payload)

        if response["Success"]==False:
            self.logger.error(f"Falha ao criar MissionExtend id {external_id}: {response}")
            raise Exception(f"Falha ao criar MissionExtend id {external_id}: {response['Description']}") 
        
        return response["InternalId"]


