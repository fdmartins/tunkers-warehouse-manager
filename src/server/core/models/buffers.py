from core import db
from datetime import datetime
import configparser
import logging
import json
from sqlalchemy import or_, and_
from ..models.buttons import ButtonCall 
from ..utils import FileRef
from ..models.mission import Mission


class Buffer:
    """
    Esta classe faz a leitura do .ini que contem a estrutura do buffer. (area, ruas e posicoes)
    """
    def __init__(self, navithor_comm):
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Iniciando Buffers")

        self.navithor_comm = navithor_comm

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
                    parts = config.get(section, key).split(';')
                    positions = list(map(int, parts[0].split(',')))
                    wait_position = int(parts[1].split('=')[1]) if len(parts) > 1 else 0
                    #positions = list(map(int, config.get(section, key).split(',')))
                    
                    ruas.append({
                        'id': int(key[3:]),  # Extrai o ID da rua
                        'positions': positions,
                        'wait_position' : wait_position
                    })
            
            section_dict['buffer_id'] = int(section)
            section_dict['rows'] = ruas
            
            # Adiciona a seção ao resultado
            self.buffers[int(section)] = section_dict


        self.logger.info(f"Arquivo de configuracao de buffers carregado.")

        #self.logger.info(json.dumps(self.buffers, indent=4) )


    def get_actual_missions_moving(self, requesting_btn_id, load_tag):

        self.logger.info(f"id({requesting_btn_id}) get_actual_missions_moving()")
        

        #navithor_missions = self.navithor_comm.get_mission_status() 

        actual_moving = {}

        # retorna os steps de missoes não finalizadas.

        button_calls = ButtonCall.query.filter(
                                                or_(
                                                    #ButtonCall.mission_status=='PENDENTE',
                                                    ButtonCall.mission_status=='EXECUTANDO'
                                                )
                                            ).all()


        for b in button_calls:
            positions = b.get_reserved_pos()

            self.logger.info(f"...call {b.id} = reserved_pos: {positions}")

            reserved_pos = None

            if len(positions)!=0:

                if load_tag:
                    # posicao de carga. sempre posicao 0 da lista.
                    reserved_pos = positions[0]
                else:
                    # posicao de descarga. sempre posicao 1 da lista.
                    reserved_pos = positions[1]

                if b.id == requesting_btn_id:
                    # proprio chamado, ignora.
                    continue

        
                area_id, row_id = self.find_area_and_row_of_position(reserved_pos)

                self.logger.info(f"Tem Missao para posicao {reserved_pos} (area {area_id} rua {row_id}) - chamado id {b.id} ")

                actual_moving.setdefault((area_id, row_id), 0)
                actual_moving[area_id, row_id]+=1


        
        return actual_moving
    
    def get_wait_pos_by_area_and_row(self, area_id, row_id):
        if area_id==None:
            return None
        
        buffer = self.get_buffer_by_id(area_id)
        
        for row in buffer['rows']:
            if row["id"] == row_id:
                if row["wait_position"]!=0:
                    return row["wait_position"]

        return None

    def get_wait_pos_of(self, pos):
        area_id, row_id = self.find_area_and_row_of_position(pos)
        
        wait_pos = self.get_wait_pos_by_area_and_row(area_id, row_id)

        if wait_pos==None:
            return pos

        return wait_pos

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

    def get_occupied_pos_of_sku(self, btn, sku, buffers_allowed):
        requesting_btn_id = btn.id


        self.logger.info(f"id({requesting_btn_id}) get_occupied_pos_of_sku({sku})")

        
        # retorna a primeira posicao acessivel pela rua.
        # actual_moving_row informa para quais area_id e row_id tem serviço sendo executado e a quantidade. ex: { (1,2):2 }  = area_id 1 rua 2 com 2 movimentos.
        actual_moving_row = self.get_actual_missions_moving(requesting_btn_id, load_tag=True)

        all_ret = BufferSKURow.query.filter_by(sku=sku).all()

        if len(all_ret)==0:
            self.logger.debug(f"id({requesting_btn_id}) Não encontrado  rua com SKU {sku}")
            return None, None
        
        
        # fazemos uma pré varredura, para saber quais ruas tem agv se movimentando. Selecionamos aquela livre.
        # isso só é util quando mais de uma rua com mesmo sku e mesmo buffer, caso do CARRETEL VAZIO.
        best_row = None
        for ret in all_ret:
            if ret.area_id in buffers_allowed:
                current_movements = actual_moving_row.get((ret.area_id, ret.row_id), 0)
                row = self.get_row_positions(ret.area_id, ret.row_id)
                occupied_positions = sum(1 for item in row if item['occupied'])
            
                if current_movements >= occupied_positions:
                    # nunca deve ser MAIOR, mas consideramos >=.
                    # ja tem agvs se movimentando para esta rua e que comprometerá as posicoes.
                    continue

                if current_movements==0:
                    best_row = ret.row_id
                    break

        self.logger.info(f"id({requesting_btn_id}) Melhor rua sem movimento {best_row} de pos CHEIA")

        # selecionamos de fato qual rua retornaremos...
        for ret in all_ret:
            if ret.area_id in buffers_allowed:
                
                if best_row!=None:
                    # existe uma possibilidade.
                    if best_row!=ret.row_id:
                        # nao é essa, continuamos...
                        continue
                
                
                row = self.get_row_positions(ret.area_id, ret.row_id)

                # Verifica se a quantidade de movimentos na rua atual é maior ou igual às posições ocupadas
                current_movements = actual_moving_row.get((ret.area_id, ret.row_id), 0)

                # se ja existe agv em movimento nesta rua, tentamos uma proxima.

                occupied_positions = sum(1 for item in row if item['occupied'])
            
                if current_movements >= occupied_positions:
                    # nunca deve ser MAIOR, mas consideramos >=.
                    # ja tem agvs se movimentando para esta rua e que comprometerá as posicoes.
                    continue
                
                # varremos a rua da direita para esquerda até encontrar a primeira posicao OCUPADA.
                for item in reversed(row):
                    if item['occupied']==True:
                        self.logger.info(f"id({requesting_btn_id}) posicao ocupada escolhida: {item['pos']} area {ret.area_id}")
                        return item['pos'], ret.area_id
            
            
        return None, None

    def is_row_with_sku_editable(self, area_id, row_id):
        # Tenta encontrar a entrada existente para o area_id e row_id
        buffer_row = BufferSKURow.query.filter_by(area_id=area_id, row_id=row_id).first()

        if buffer_row:
            if buffer_row.fixed==1:
                return False
            else:
                return True
            
        return True


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
            
    def get_free_pos(self, btn, sku, buffers_allowed):
        """
        Encontra uma posição livre para um SKU respeitando a prioridade sequencial dos buffers permitidos
        Args:
            sku: SKU do produto
            buffers_allowed: Lista de buffers permitidos por prioridade sequencial desta lista.
        Returns:
            tuple: (position_id, area_id) ou (None, None) se não encontrar posição
        """
        # Para cada buffer na ordem de prioridade
        for b_a in buffers_allowed:
            free_pos_id, free_area_id  = self.get_free_pos_first(btn, sku, [b_a, ])
            if free_pos_id!=None and free_area_id!=None:
                return free_pos_id, free_area_id
            
        return None, None


    def get_free_pos_first(self, btn, sku, buffers_allowed):
        """
        retorna a primeira posicao vazia da rua do buffer. 
        Aqui a ordem é pela sequencia dos id dos buffers, sem respeitar a ordem da lista buffers_allowed
        """

        requesting_btn_id = btn.id

        self.logger.info(f"id({requesting_btn_id}) get_free_pos({sku})  buffers={buffers_allowed}")

        # actual_moving_row informa para quais area_id e row_id tem serviço sendo executado e a quantidade. ex: { (1,2):2 }  = area_id 1 rua 2 com 2 movimentos.
        actual_moving_row = self.get_actual_missions_moving(requesting_btn_id, load_tag=False)


        free_pos_id = None
        free_area_id = None 

        ret_all = BufferSKURow.query.filter_by(sku=sku).all()


        # fazemos uma pré varredura, para saber quais ruas tem agv se movimentando. Selecionamos aquela livre.
        # isso só é util quando mais de uma rua com mesmo sku e mesmo buffer, caso do CARRETEL VAZIO.
        best_row = None
        for ret in ret_all:
            if ret.area_id in buffers_allowed:
                current_movements = actual_moving_row.get((ret.area_id, ret.row_id), 0)
                row = self.get_row_positions(ret.area_id, ret.row_id)
                empty_positions = sum(1 for item in row if not item['occupied'])
            
                if current_movements >= empty_positions:
                    # nunca deve ser MAIOR, mas consideramos >=.
                    # ja tem agvs se movimentando para esta rua e que comprometerá as posicoes.
                    continue

                if current_movements==0:
                    best_row = ret.row_id
                    break

        self.logger.info(f"id({requesting_btn_id}) Melhor rua sem movimento {best_row} de pos VAZIA")

        for ret in ret_all:

            if best_row!=None:
                # existe uma possibilidade.
                if best_row!=ret.row_id:
                    # nao é essa, continuamos...
                    continue

            row = self.get_row_positions(ret.area_id, ret.row_id)
            current_movements = actual_moving_row.get((ret.area_id, ret.row_id), 0)
            empty_positions = sum(1 for item in row if not item['occupied'])

            #self.logger.info(actual_moving_row)
            self.logger.info(f"id({requesting_btn_id}) {empty_positions} posicoes livres para area {ret.area_id} rua {ret.row_id}")
            self.logger.info(f"id({requesting_btn_id}) {current_movements} Movimentos correntes para area {ret.area_id} rua {ret.row_id}")

            if current_movements >= empty_positions:
                continue

            # este sku ja tem em alguma rua...
            free_pos_id_test, free_area_id_test = self.get_first_free_pos_in_row(ret.area_id, ret.row_id)

            # verificamos se esta em um buffer id permitido.
            if free_pos_id_test!=None and free_area_id_test in buffers_allowed:
                self.logger.info(f"id({requesting_btn_id}) Encontrado SKU {sku} no buffer {ret.area_id} rua {ret.row_id}")
                free_pos_id = free_pos_id_test
                free_area_id = free_area_id_test
                break


        #self.logger.debug(f"{len(ret_all)} {free_area_id}")

        if len(ret_all)==0 or free_area_id==None:
            self.logger.info(f"id({requesting_btn_id}) Tentando encontrar nova rua para sku {sku}...")
            for area_id, buffer in self.buffers.items():
                for area_id in buffers_allowed:
                    for row in buffer['rows']:
                        ret = BufferSKURow.query.filter_by(area_id=area_id, row_id=row["id"]).one_or_none()
                        if ret==None:
                            row_positions = self.get_row_positions(area_id, row["id"])
                            if row_positions==None:
                                continue

                            current_movements = actual_moving_row.get((area_id, row["id"]), 0)
                            empty_positions = sum(1 for item in row_positions if not item['occupied'])
                            
                            if current_movements >= empty_positions:
                                continue

                            free_pos_id, free_area_id = self.get_first_free_pos_in_row(area_id, row["id"])
                            if free_pos_id!=None:
                                # nesse buffer e nessa rua foi encontrado posicao livre.
                                self.logger.info(f"id({requesting_btn_id}) Encontrado Rua Livre no buffer {free_area_id} posicao {free_pos_id}")
                                return free_pos_id, free_area_id 

            self.logger.error(f"id({requesting_btn_id})  Nao existe rua livre para dedicarmos um o sku {sku}!")

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

    def clear_all_positions_of_row(self, area_id, row_id):
        self.logger.info(f"Limpando todas posicoes do buffer {area_id} rua {row_id}")
        # remove todas ocupacoes associadas.
        re = BufferPositions.query.filter_by(area_id=area_id, row_id=row_id).all()
        for r in re:
            self.logger.warning(f"Buffer {r.area_id}: Liberado rua {r.row_id} posicao {r.pos_id}")
            db.session.delete(r)

        

    def set_sku_to_row(self, area_id, row_id, sku):

        try:
            # Tenta encontrar a entrada existente para o area_id e row_id
            buffer_row = BufferSKURow.query.filter_by(area_id=area_id, row_id=row_id).first()

            if buffer_row:
                if buffer_row.fixed==1:
                    # podemos limpar as posicoes, mas nao trocar o sku!!
                    if sku is None:
                        self.clear_all_positions_of_row(area_id, row_id)
                        
                    return False, "Esta posição é protegida. Não pode trocar o SKU."

            if sku is None:
                self.logger.info(f"Setando Sku None para {area_id} {row_id}")

                self.clear_all_positions_of_row(area_id, row_id)

                if buffer_row:
                    # remove o sku da rua.
                    db.session.delete(buffer_row)
                   
            else:
                self.logger.info(f"Setando Sku {sku} para {area_id} {row_id}")

                if buffer_row:
                    # Se existir, atualiza o SKU e o horário de ocupação
                    buffer_row.sku = sku
                    buffer_row.dt_occupation = datetime.now()
                else:
                    # Caso contrário, cria uma nova entrada
                    new_row = BufferSKURow(
                        area_id=area_id,
                        row_id=row_id,
                        sku=sku,
                        dt_occupation=datetime.now()
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
                
                if pos_id == row["wait_position"]:
                    return area_id, row["id"]
                
        return None, None

    def set_position_ocupation_by_tag_pos(self, pos_id, occupied):
        self.logger.info(f"Marcando Posicao {pos_id} com occupied={occupied}")

        # descobrimos de qual area_id e row_id esta posicao pertence.
        area_id, row_id = self.find_area_and_row_of_position(pos_id)

        if area_id==None:
            self.logger.error(f"Não encontrada posicao {pos_id} em nenhum buffer configurado!!")
            raise Exception(f"Não encontrada posicao {pos_id} em nenhum buffer configurado!!")
        

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
    dt_occupation = db.Column(db.DateTime, default=datetime.now) # horário que essa fila assumiu esse sku pela primeira vez.
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

    dt_occupation = db.Column(db.DateTime, default=datetime.now) # horario que a posicao foi ocupada.

    