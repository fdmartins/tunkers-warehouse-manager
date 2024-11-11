from flask import Flask, request, jsonify
import random
import string

app = Flask(__name__)

# Contador global para LoadCount
request_counter = 0

# Dicionário para armazenar o estado dos positions
position_states = {}

def generate_random_token(length=32):
    """Gera um token aleatório"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_internal_id():
    """Gera um ID interno aleatório"""
    return f"ID-{''.join(random.choice(string.digits) for _ in range(8))}"

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
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)