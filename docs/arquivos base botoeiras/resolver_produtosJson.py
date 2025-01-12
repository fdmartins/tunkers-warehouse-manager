import json
from typing import Dict, List

def flatten_json_structure(data: Dict) -> List[Dict]:
    """
    Converte a estrutura JSON hierárquica em uma lista de dicionários planos.
    """
    flattened_data = []
    
    for thickness, products in data['Produtos'].items():
        for product_name, details in products.items():
            row = {
                'bitola': thickness,
                'nome': product_name.strip(),
                'sku': details['SKU'],
                'tipo': details['material_type']
            }
            flattened_data.append(row)
    
    return flattened_data

def generate_insert_commands(data: List[Dict]) -> List[str]:
    """
    Gera os comandos SQL INSERT a partir dos dados planificados.
    """
    insert_commands = []
    
    # Comando base para o INSERT com o novo campo bitola
    insert_template = (
        'INSERT INTO produtos_resumido (bitola, nome, sku, tipo) '
        "VALUES ('{bitola}', '{nome}', '{sku}', '{tipo}');"
    )
    
    for row in data:
        # Escapa aspas simples nos valores para evitar erros no SQL
        nome = row['nome'].replace("'", "''")
        tipo = row['tipo'].replace("'", "''")
        
        # Gera o comando INSERT
        insert_command = insert_template.format(
            bitola=row['bitola'],
            nome=nome,
            sku=row['sku'],
            tipo=tipo
        )
        insert_commands.append(insert_command)
    
    return insert_commands

def convert_json_to_sql(input_file: str, output_file: str):
    """
    Lê o arquivo JSON hierárquico e gera um arquivo TXT com comandos SQL INSERT.
    
    Args:
        input_file (str): Caminho do arquivo JSON de entrada
        output_file (str): Caminho do arquivo TXT de saída
    """
    try:
        # Lê o arquivo JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Aplana a estrutura
        flattened_data = flatten_json_structure(data)
        
        # Gera os comandos INSERT
        insert_commands = generate_insert_commands(flattened_data)
        
        # Escreve os comandos no arquivo TXT
        with open(output_file, 'w', encoding='utf-8') as f:
            # Adiciona um comentário inicial
            f.write("-- Comandos SQL para inserção de produtos\n")
            f.write("-- Gerado automaticamente a partir de estrutura hierárquica\n")
            f.write("-- Tabela: produtos_resumido\n\n")
            
            # Escreve cada comando em uma nova linha
            for command in sorted(insert_commands):  # Ordena os comandos
                f.write(command + '\n')
        
        print("Arquivo SQL gerado com sucesso!")
        
    except FileNotFoundError:
        print("Erro: Arquivo JSON de entrada não encontrado.")
    except json.JSONDecodeError:
        print("Erro: O arquivo JSON está mal formatado.")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {str(e)}")

def main():
    convert_json_to_sql('produtos.json', 'inserts_produtos_resumido.sql')

if __name__ == "__main__":
    main()