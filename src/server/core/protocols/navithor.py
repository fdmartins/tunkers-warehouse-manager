import logging
import requests

from .defines import StepType
import threading
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import configparser
from ..utils import FileRef

class ThreadSafeRequests:
    def __init__(self):
        self._lock = threading.Lock()
        self._session = requests.Session()
        MAX_POOL_SIZE = 2
        adapter = HTTPAdapter(pool_connections=MAX_POOL_SIZE, pool_maxsize=MAX_POOL_SIZE)
        self._session .mount("http://", adapter)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        with self._lock:
            return self._session.get(url, **kwargs)
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        with self._lock:
            return self._session.post(url, data=data, **kwargs)
    
    def __del__(self):
        self._session.close()


class Navithor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Cria um objeto ConfigParser
        config = configparser.ConfigParser()

        # Lê o arquivo de configuração
        config.read(FileRef.get_path('./configs/navithor.ini'))

        ip = config.get("comm", 'ip')
        port = config.get("comm", 'port')

        self.fake = False
        self.fake_pos_occupation = {}

        self.ip = ip
        self.port = port

        self.logger.info(f"Iniciando Protocolo API Navithor IP {ip} porta {port}")

        self.requester = ThreadSafeRequests()

        self.logger.info(f"Iniciado OK")

        self.access_token = None

        try:
            self.updateAuthToken()
        except Exception as err:
            self.logger.error("Falha atualizacao token autenticacao navithor: " + str(err))

    def call_api(self, endpoint, payload={}, headers=None, method="POST"):

        if self.fake: return {}

        try:

            if self.access_token==None:
                self.logger.warning("Access Token NULO (erro de comm anteriormente?)")

            if headers==None:
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    "Content-Type": "application/json"
                }
            
            # Faz a requisição POST para a API
            if method=="POST":
                if headers["Content-Type"]=="application/x-www-form-urlencoded":
                    #self.logger.debug("application/x-www-form-urlencoded")
                    response = self.requester.post(f"http://{self.ip}:{self.port}{endpoint}", data=payload, headers=headers)
                else:
                    response = self.requester.post(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)
            else:
                response = self.requester.get(f"http://{self.ip}:{self.port}{endpoint}", json=payload, headers=headers)

            
        except Exception as e:
            self.logger.error(f"Falha request navithor {e}")

            # limpamos o token para refazer no proximo ciclo (navithor provavelmente guarda em memoria , e quando é reiniciado perde a autorizacao.)
            self.access_token=None

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

    def needAuthToken(self):
        if self.access_token==None:
            return True
        return False

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

        #self.logger.info(f"Versão Navithor: {response} ")


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

        if ("success" not in response) and ("Success" not in response):
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


    def extend_mission(self, id_local=None, steps=None):
        self.logger.info("Enviando Extensão da Missão ao Navithor...")
        #return external_id
    
        endpoint = "/api/MissionExtend"

        # Define o payload
        payload = {
            "ExternalId": id_local,
            "Steps": steps
        }

        response =  self.call_api(endpoint, payload)

        if ("success" not in response) and ("Success" not in response):
            raise Exception(f"Falha Comunicação NAVITHOR - ao criar MissionExtend id {id_local}: {response}") 

        if response["Success"]==False:
            self.logger.error(f"Falha ao criar MissionExtend id {id_local}: {response}")
            raise Exception(f"Falha ao criar MissionExtend id {id_local}: {response['Description']}") 
        
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

        if ("success" not in response) and ("Success" not in response):
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
    

    def abort_mission(self, id_local):
        if self.fake: 
            return

        endpoint = "/api/MissionAbort" 
        

        payload = {
            "ExternalId": id_local,
        }

        self.logger.debug(payload)

        response =  self.call_api(endpoint, payload, method="POST")

        if response["Success"]==False:
            self.logger.error(f"Falha ao abortar missão id {id_local}: {response}")
            raise Exception(f"Falha ao abortar missão id {id_local}: {response}") 
        
        return False
        

