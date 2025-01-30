from flask import Flask, request, jsonify
import random
import string
import datetime

app = Flask(__name__)

# Contador global para LoadCount
request_counter = 0

# Dicionário para armazenar o estado dos positions
position_states = {}

missions = {
    101: {
        'ExternalId': 101, 'Name': 'Gerenciador Tunkers', 'Options': {'Priority': 3}, 
        'Steps': [
            {'StepType': 'Pickup', 'Options': {'SortingRules': ['Priority', 'Closest'], 'WaitForExtension': False}, 'AllowedTargets': [{'Id': 5007}], 'AllowedWaits': [], 'StepStatus': 'inserido', 'CurrentTargetId': 5007},
            {'StepType': 'Dropoff', 'Options': {'SortingRules': ['Priority', 'Closest'], 'WaitForExtension': False}, 'AllowedTargets': [{'Id': 250}], 'AllowedWaits': [], 'StepStatus': 'inserido', 'CurrentTargetId': 250}
            ], 
            
            'State': "Inserido", 'Id': 101, 'InternalId': 101, 'AssignedMachineId': -1, 'CurrentStepIndex': 0} 
            
            }

missions = {}

def generate_random_token(length=32):
    """Gera um token aleatório"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_internal_id():
    """Gera um ID interno aleatório"""
    return f"{''.join(random.choice(string.digits) for _ in range(8))}"

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path=""):
    global request_counter
    request_counter += 1
    
    # Tratamento especial para a rota /api/LoadAtLocation
    if path == "api/LoadAtLocation" and request.method == 'POST':
        try:
            data = request.json
            position = data.get('symbolicPointId')
            amount = data.get('amount')
            
            # Armazena o amount para o position específico
            position_states[position] = amount
            
            print(f"Estado atualizado - Position {position}: {amount}")  # Debug info
            print(f"Estado atual: {position_states}")  # Debug info
            
        except Exception as e:
            return jsonify({
                "InternalId": generate_internal_id(),
                "LoadCount": request_counter,
                "access_token": generate_random_token(),
                "success": False,
                "error": str(e)
            })
    
    response_data = {
        "InternalId": generate_internal_id(),
        "LoadCount": request_counter,
        "access_token": generate_random_token(),
        "success": True,
        "Success": True,
        "Id":0
    }
    
    # Para LoadAtLocation, incluímos o estado atual do position na resposta
    if path == "api/LoadAtLocation" and request.method == 'GET':
        response_data["LoadCount"] = position_states.get(request.json.get('symbolicPointId'))

    if path == "api/missioncreate":

        #if request.json.get('ExternalId') in missions:


        missions.setdefault(request.json.get('ExternalId'), request.json)

        print(request.json)

        steps = request.json.get('Steps')

        for s in steps:
            if "StepStatus" not in s:
                s["StepStatus"] = "inserido"

        
        
        missions[request.json.get('ExternalId')]['State'] = request.json.get('State')
        missions[request.json.get('ExternalId')]['Id'] = request.json.get('ExternalId')
        missions[request.json.get('ExternalId')]['InternalId'] = request.json.get('ExternalId')
        missions[request.json.get('ExternalId')]['Steps'] = steps
        missions[request.json.get('ExternalId')]['Date'] = datetime.datetime.now()

        response_data = {"Success":True, 'InternalId':request.json.get('ExternalId'),   'ExternalId': request.json.get('ExternalId') }



    if path == "api/MissionExtend":
        missions.setdefault(request.json.get('ExternalId'), request.json)


        if request.json.get('ExternalId') in missions:
            missions[request.json.get('ExternalId')]["State"] = "Executing"

            steps = request.json.get('Steps')

            for s in steps:
                if "StepStatus" not in s:
                    s["StepStatus"] = "inserido"

            for s in steps:
                missions[request.json.get('ExternalId')]['Steps'].append(s)
                
            #missions[request.json.get('ExternalId')]['State'] = 'Inserido'
            #missions[request.json.get('ExternalId')]['Id'] = request.json.get('ExternalId')
            #missions[request.json.get('ExternalId')]['InternalId'] = request.json.get('ExternalId')

        response_data = {"Success":True, 'InternalId':request.json.get('ExternalId'),   'ExternalId': request.json.get('ExternalId') }



    if path == "api/GetMissions":
        
        
        #for m_id in missions:
        #    if missions[m_id]["State"]=="Completed" and (datetime.datetime.now()-missions[m_id]["Date"]).total_seconds()>5:
        #        missions.pop(m_id, None)

        response_data = []
        
        for m in missions.keys():
            print(missions[m])

            missions[m]['AssignedMachineId']=-1
            missions[m]['CurrentStepIndex']=0
            
            for s in missions[m]['Steps']:
                s['CurrentTargetId'] = s['AllowedTargets'][0]["Id"]
            
            response_data.append(missions[m])

        
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)