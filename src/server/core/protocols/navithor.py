import logging
import requests

from .defines import StepType

class Navithor:
    def __init__(self, ip="127.0.0.1", port=1234):
        self.logger = logging.getLogger(__name__)

        self.fake = True
        self.fake_pos_occupation = {}

        self.ip = ip
        self.port = port

        self.logger.info(f"Iniciado Protocolo API Navithor IP {ip} porta {port}")

        self.access_token = None

        try:
            self.updateAuthToken()
        except Exception as err:
            self.logger.error("Falha atualizacao token autenticacao navithor: " + str(err))

    def call_api(self, endpoint, payload={}, headers=None, method="POST"):

        if self.fake: return {}

        if headers==None:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                "Content-Type": "application/json"
            }
        
        #self.logger.debug(headers)

        try:
            # Faz a requisição POST para a API
            if method=="POST":
                if headers["Content-Type"]=="application/x-www-form-urlencoded":
                    #self.logger.debug("application/x-www-form-urlencoded")
                    response = requests.post(f"http://{self.ip}:{self.port}{endpoint}", data=payload, headers=headers)
                else:
                    response = requests.post(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)
            else:
                response = requests.get(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)
        except Exception as e:
            raise Exception(f"Falha Comunicação NAVITHOR - {e}") 

        self.logger.debug(response.json())

        return response.json()
    
        # Verifica se a resposta foi bem-sucedida
        #if response.status_code == 200:
        #    return response.json()
        #else:
        #    return {"error": f"Erro na requisição: {response.status_code}"}
        
    def checkVersion(self):
        endpoint = "/api/getVersion"
 
        return self.call_api(endpoint, method="GET")


    def updateAuthToken(self):
        if self.fake: return False

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
        
        if self.fake: return id_local
        
        endpoint = "/api/missioncreate"

        payload = {
            "ExternalId": id_local,
            "Name": "Gerenciador Tunkers",
            "Options": {
                "Priority": 3
            },
            "Steps": steps
        }

        self.logger.debug(payload)
        #exit()

        response =  self.call_api(endpoint, payload)

        if ("success" not in response) or ("Success" not in response):
            raise Exception(f"Falha Comunicação NAVITHOR - ao criar missão id {id_local}: {response}") 

        if response["Success"]==False:
            self.logger.error(f"Falha ao criar missão id {id_local}: {response}")
            raise Exception(f"Falha ao criar missão id {id_local}: {response['Description']}") 
        
        return response["InternalId"]

 
    def get_mission_status(self):
        #return []
        #self.logger.debug("Verificando Status das Missões...")

        #endpoint = "/api/MissionStatusRequest"
        endpoint = "/api/GetMissions" # retorna mais ifnormacoes uteis, como o passo que esta sendo executado!!)
        
        response = self.call_api(endpoint, method="GET")

        #for m in response:
        #    if m["ExternalId"]==external_id:
        #        return m
            
        return response


    def extend_mission(self, external_id=None, steps=None):
        self.logger.info("Enviando Extensão da Missão ao Navithor...")
        #return external_id
    
        endpoint = "/api/MissionExtend"

        # Define o payload
        payload = {
            "ExternalId": external_id,
            "Steps": steps
        }

        response =  self.call_api(endpoint, payload)

        if ("success" not in response) or ("Success" not in response):
            raise Exception(f"Falha Comunicação NAVITHOR - ao criar MissionExtend id {external_id}: {response}") 

        if response["Success"]==False:
            self.logger.error(f"Falha ao criar MissionExtend id {external_id}: {response}")
            raise Exception(f"Falha ao criar MissionExtend id {external_id}: {response['Description']}") 
        
        return response["InternalId"]


    def set_position_occupation(self, position, occupied):
        self.logger.info(f"Marcando posicao {position} com ocupacao={occupied}...")

        if self.fake: 
            self.fake_pos_occupation.setdefault(position, occupied)
            return True

        endpoint = "/api/LoadAtLocation" 
        

        payload = {
            "symbolicPointId": position,
            "resourceType":1,
            "amount": 1 if occupied else 0
        }

        self.logger.debug(payload)

        response =  self.call_api(endpoint, payload)

        if ("success" not in response) or "Success" not in response:
            raise Exception(f"Falha Comunicação NAVITHOR - ao mudar status da ocupação da posicao {position}: {response}") 

        if response["success"]==False:
            self.logger.error(f"NAVITHOR NAO RETORNO SUCESSO AO MUDAR STATUS DE OCUPACAO DA POSICAO {position} {response}")

    def get_position_occupation(self, position):
        #self.logger.debug(f"Buscando status de ocupacao da posicao {position}...")

        if self.fake: 
            if position not in self.fake_pos_occupation:
                return False
            
            return self.fake_pos_occupation[position]

        endpoint = "/api/LoadAtLocation" 
        

        payload = {
            "symbolicPointId": position,
        }

        self.logger.debug(payload)

        response =  self.call_api(endpoint, payload, method="GET")

        if "LoadCount" not in response:
            raise Exception(f"Falha Comunicação NAVITHOR - ao buscar status da ocupação da posicao {position}: {response}") 
        
        if response["LoadCount"]!=0:
            return True

        return False

        

