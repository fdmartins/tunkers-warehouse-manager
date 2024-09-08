from core import db
from datetime import datetime
import configparser
import logging
import json 

class Buffer:
    """
    Esta classe faz a leitura do .ini que contem a estrutura do buffer. (area, ruas e posicoes)
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Cria um objeto ConfigParser
        config = configparser.ConfigParser()

        # Lê o arquivo de configuração
        config.read('buffer.ini')

        #self.buffers = {section: dict(config.items(section)) for section in config.sections()}

        self.buffers = {}
        
        for section in config.sections():
            # Converte a seção em um dicionário
            section_dict = {}
            section_dict['titulo_area'] = config.get(section, 'titulo_area')
            
            ruas = []
            for key in config[section]:
                if key.startswith('rua'):
                    # Obtém a lista de posições para cada rua
                    positions = list(map(int, config.get(section, key).split(',')))
                    ruas.append({
                        'id': int(key[3:]),  # Extrai o ID da rua
                        'positions': positions
                    })
            
            section_dict['buffer_id'] = int(section)
            section_dict['rows'] = ruas
            
            # Adiciona a seção ao resultado
            self.buffers[int(section)] = section_dict


        self.logger.info(f"Arquivo de configuracao de buffers carregado.")

        self.logger.info(json.dumps(self.buffers, indent=4) )


    def get_buffer_by_id(self, area_id):
        # retorna apenas a estrutura, sem status das posicoes.
        if area_id not in self.buffers:
            return {}
        return self.buffers[area_id]
    

    def get_buffer_occupied_by_id(self, area_id):
        # retorna a estrutura junto se a posicao esta ocupada ou nao.

        # buscamos a estrutura configurada.
        buffer = self.get_buffer_by_id(area_id)

        buffer_view = []
        for row in buffer['rows']:
            
            # verificamos as ruas com sku definido no banco (descarregados automaticamente)
            ret = BufferSKURow.query.filter_by(area_id=area_id, row_id=row["id"]).one_or_none()
            
            sku = None
            if ret!=None:
                sku = ret.sku

            # verificamos as posicoes ocupadas no banco (descarregados automaticamente)
            ret_positions_occupied = BufferPositions.query.filter_by(area_id=area_id, row_id=row["id"]).all()

            positions_occupied = {}
            for p in ret_positions_occupied:
                positions_occupied.setdefault(p.pos_id, p.dt_occupation)

            positions = []

            for pos in row["positions"]:
                occupied = False
                dt_occupation = None
                if pos in positions_occupied.keys():
                    occupied = True
                    dt_occupation =positions_occupied[pos]
                
                positions.append({
                    "pos": pos,
                    "occupied": occupied,
                    "occupation_date": dt_occupation
                })

            buffer_view.append({
                "row_id": row["id"],
                "sku": sku, 
                "positions": positions                
            })

        return buffer_view


    def set_sku_to_row(self, area_id, row_id, sku):

        try:
            # Tenta encontrar a entrada existente para o area_id e row_id
            buffer_row = BufferSKURow.query.filter_by(area_id=area_id, row_id=row_id).first()

            if sku is None:
                if buffer_row:
                    # Se o registro existe e o SKU é None, remove o registro
                    db.session.delete(buffer_row)
            else:
                if buffer_row:
                    # Se existir, atualiza o SKU e o horário de ocupação
                    buffer_row.sku = sku
                    buffer_row.dt_occupation = datetime.utcnow()
                else:
                    # Caso contrário, cria uma nova entrada
                    new_row = BufferSKURow(
                        area_id=area_id,
                        row_id=row_id,
                        sku=sku,
                        dt_occupation=datetime.utcnow()
                    )
                    db.session.add(new_row)
            
            # Commit para salvar as alterações
            db.session.commit()
            return True

        except Exception as e:
            logging.error(e)
            return False


    def set_position_occupation(self, area_id, row_id, pos_id, occupied):
        try: 
            # Tenta encontrar a entrada existente para o area_id, row_id, e pos_id
            position = BufferPositions.query.filter_by(area_id=area_id, row_id=row_id, pos_id=pos_id).first()

            if occupied:
                if not position:
                    # Se a posição não existir, cria uma nova entrada
                    new_position = BufferPositions(
                        area_id=area_id,
                        row_id=row_id,
                        pos_id=pos_id
                    )
                    db.session.add(new_position)
            else:
                if position:
                    # Se a posição existir e occupied=false, remove a entrada
                    db.session.delete(position)
            
            # Commit para salvar as alterações
            db.session.commit()
            return True
        
        except Exception as e:
            logging.error(e)
            return False

class BufferSKURow(db.Model):
    """
    esta tabela armazena as ruas que foram cativadas para determinado SKU.
    se a rua não tem nenhum produto. Ela é removida desta lista.
    """
    id = db.Column(db.Integer, primary_key=True)

    area_id = db.Column(db.Integer, nullable=False)
    row_id = db.Column(db.Integer, nullable=False)   
    sku = db.Column(db.String(32), nullable=False)  
    dt_occupation = db.Column(db.DateTime, default=datetime.utcnow) # horário que essa fila assumiu esse sku pela primeira vez.

    


class BufferPositions(db.Model):
    """
        esta tabela armazena as posicoes ocupadas da rua.
      Quando a posicao é desocupada, a linha será removida desta tabela.
    """
    id = db.Column(db.Integer, primary_key=True)

    area_id = db.Column(db.Integer, nullable=False)
    row_id = db.Column(db.Integer, nullable=False) 
    pos_id = db.Column(db.Integer, nullable=False)  # posicao/tag do buffer

    dt_occupation = db.Column(db.DateTime, default=datetime.utcnow) # horario que a posicao foi ocupada.

    