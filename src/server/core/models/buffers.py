from core import db
from datetime import datetime
import configparser
import logging
import json 
from ..utils import FileRef

class Buffer:
    """
    Esta classe faz a leitura do .ini que contem a estrutura do buffer. (area, ruas e posicoes)
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Iniciando Buffers")

        # Cria um objeto ConfigParser
        config = configparser.ConfigParser()

        # Lê o arquivo de configuração
        config.read(FileRef.get_path('./configs/buffer.ini'))

        #self.buffers = {section: dict(config.items(section)) for section in config.sections()}

        self.buffers = {}
        
        for section in config.sections():
            # Converte a seção em um dicionário
            section_dict = {}
            section_dict['titulo_area'] = config.get(section, 'titulo_area')
            section_dict['type'] = config.get(section, 'tipo')
            
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



    def get_row_positions(self, area_id, row_id):
        buffer = self.get_buffer_by_id(area_id)
        
        
        for row in buffer['rows']:
            if row["id"] == row_id:

                ret_positions_occupied = BufferPositions.query.filter_by(area_id=area_id, row_id=row_id).all()

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

                return positions
            
        return None

    def get_occupied_pos_of_sku(self, sku, buffers_allowed):
        # retorna a primeira posicao acessivel pela rua.

        all_ret = BufferSKURow.query.filter_by(sku=sku).all()

        if len(all_ret)==0:
            self.logger.debug(f"Não encontrado nenhuma rua com SKU {sku}")
            return None, None
        
        for ret in all_ret:
            if ret.area_id in buffers_allowed:
                row = self.get_row_positions(ret.area_id, ret.row_id)
                
                # varremos a rua da direita para esquerda até encontrar a primeira posicao OCUPADA.
                for item in reversed(row):
                    if item['occupied']==True:
                        return item['pos'], ret.area_id
            
        return None, None

    def get_sku_from_row(self, area_id, row_id):
        all_ret = BufferSKURow.query.filter_by(area_id=area_id, row_id=row_id).all()

        if len(all_ret)!=0:
            return all_ret[0].sku

        return None


    def get_first_free_pos_in_row(self, area_id, row_id):
        row = self.get_row_positions(area_id, row_id)
        
        # encontramos a primeira ocorrência ao varrer a lista de trás para frente:
        ultima_livre = None, None

        if row==None:
            return ultima_livre

        for item in reversed(row):
            if item['occupied']==False:
                ultima_livre = item['pos'], area_id
            else:
                break  # Parar ao encontrar o primeiro 'occupied=True'

        return ultima_livre
            
    

    def get_free_pos(self, sku, buffers_allowed):
        free_pos_id = None
        free_area_id = None 

        ret_all = BufferSKURow.query.filter_by(sku=sku).all()


        if len(ret_all)==0:
            self.logger.debug("não existe ainda uma rua com este sku, pegamos uma rua livre e a dedicamos para o sku")
            for area_id, buffer in self.buffers.items():
                for area_id in buffers_allowed:
                    for row in buffer['rows']:
                        ret = BufferSKURow.query.filter_by(area_id=area_id, row_id=row["id"]).one_or_none()
                        if ret==None:
                            free_pos_id, free_area_id = self.get_first_free_pos_in_row(area_id, row["id"])
                            if free_pos_id!=None:
                                # nesse buffer e nessa rua foi encontrado posicao livre.
                                self.logger.debug(f"Encontrado Rua Livre no buffer {free_area_id} posicao {free_pos_id}")
                                return free_pos_id, free_area_id 
            
        
        for ret in ret_all:
            free_pos_id, free_area_id = self.get_first_free_pos_in_row(ret.area_id, ret.row_id)
            if free_pos_id!=None and free_area_id in buffers_allowed:
                break

            
        return free_pos_id, free_area_id 
    
    def clear_sku_row_with_no_occupation(self):
        # buscamos por todos skus cadastrados no banco...
        # buscamos por todas posicoes de cada sku. Se nao existe posicao ocupada, removemos o sku da rua.

        rows = BufferSKURow.query.filter_by(fixed=0).all()
        for r in rows:
            re = BufferPositions.query.filter_by(area_id=r.area_id, row_id=r.row_id).all()
            count = len(re)
            self.logger.debug(f"Buffer {r.area_id} Rua {r.row_id} com SKU {r.sku} - quantidade de produtos: {count}")
            if count==0:
                self.logger.info(f"Liberando rua {r.row_id} do buffer {r.area_id} - todos produto desta rua foram retirados.")
                db.session.delete(r)

        db.session.commit()

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
            positions = self.get_row_positions(area_id, row["id"])

            buffer_view.append({
                "row_id": row["id"],
                "sku": sku, 
                "type": buffer["type"] , 
                "positions": positions                
            })

        return buffer_view


    def get_all_positions_and_ocupations(self):
        positions = []
        for buffer_id in self.buffers.keys():
            #print(buffer_id)
            buffer = self.get_buffer_occupied_by_id(buffer_id)
            for row in buffer:
                #print(row["positions"])
                p = row["positions"]
                positions+=p

        return positions

    def set_sku_to_row(self, area_id, row_id, sku):

        try:
            # Tenta encontrar a entrada existente para o area_id e row_id
            buffer_row = BufferSKURow.query.filter_by(area_id=area_id, row_id=row_id).first()

            if buffer_row:
                if buffer_row.fixed==1:
                    return False, "Esta posição é protegida. Não pode trocar o SKU."

            if sku is None:
                if buffer_row:
                    
                    # Se o registro existe e o SKU é None, remove o registro

                    # remove todas ocupacoes associadas.
                    re = BufferPositions.query.filter_by(area_id=area_id, row_id=row_id).all()
                    for r in re:
                        self.logger.warning(f"Buffer {r.area_id}: Liberado rua {r.row_id} posicao {r.pos_id}")
                        db.session.delete(r)

                    # remove o registro.
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
            return True,""

        except Exception as e:
            logging.error(e)
            return False, str(e)
        
    def is_position_buffer(self, pos_id):
        for area_id, buffer in self.buffers.items():
            for row in buffer['rows']:
                if pos_id in row["positions"]:
                    return True
                
        return False

    def find_area_and_row_of_position(self, pos_id):
        for area_id, buffer in self.buffers.items():
            for row in buffer['rows']:
                if pos_id in row["positions"]:
                    return area_id, row["id"]
                
        return None, None

    def set_position_ocupation_by_tag_pos(self, pos_id, occupied):
        self.logger.info(f"Marcando Posicao {pos_id} com occupied={occupied}")

        # descobrimos de qual area_id e row_id esta posicao pertence.
        area_id, row_id = self.find_area_and_row_of_position(pos_id)

        if area_id==None:
            self.logger.error(f"Não encontrada posicao {pos_id} em nenhum buffer configurado!!")
            raise Exception("Não encontrada posicao {pos_id} em nenhum buffer configurado!!")
        

        return self.set_position_occupation(area_id, row_id, pos_id, occupied)


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
    fixed = db.Column(db.Integer, default=0)   # define se é uma rua editavel.(no banco)
    


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

    