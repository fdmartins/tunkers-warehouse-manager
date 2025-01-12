import json
from typing import Dict, List

def generate_insert_commands(data: Dict) -> List[str]:
    """
    Gera os comandos SQL INSERT a partir da estrutura JSON.
    """
    insert_commands = []
    
    # Comando base para o INSERT
    insert_template = (
        'INSERT INTO produtos_completo (sku, nome, tipo) '
        "VALUES ('{sku}', '{nome}', '{tipo}');"
    )
    
    for sku, details in data['Produtos'].items():
        # Escapa aspas simples nos valores para evitar erros no SQL
        nome = details['Nome'].replace("'", "''")
        tipo = details['material_type'].replace("'", "''")
        
        # Gera o comando INSERT
        insert_command = insert_template.format(
            sku=sku,
            nome=nome,
            tipo=tipo
        )
        insert_commands.append(insert_command)
    
    return insert_commands

def convert_json_to_sql(input_file: str, output_file: str):
    """
    Lê o arquivo JSON e gera um arquivo TXT com comandos SQL INSERT.
    
    Args:
        input_file (str): Caminho do arquivo JSON de entrada
        output_file (str): Caminho do arquivo TXT de saída
    """
    try:
        # Lê o arquivo JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Gera os comandos INSERT
        insert_commands = generate_insert_commands(data)
        
        # Escreve os comandos no arquivo TXT
        with open(output_file, 'w', encoding='utf-8') as f:
            # Adiciona um comentário inicial
            f.write("-- Comandos SQL para inserção de produtos\n")
            f.write("-- Gerado automaticamente\n\n")
            
            # Escreve cada comando em uma nova linha
            for command in sorted(insert_commands):  # Ordena os comandos pelo SKU
                f.write(command + '\n')
        
        print("Arquivo SQL gerado com sucesso!")
        
    except FileNotFoundError:
        print("Erro: Arquivo JSON de entrada não encontrado.")
    except json.JSONDecodeError:
        print("Erro: O arquivo JSON está mal formatado.")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {str(e)}")

def main():
    convert_json_to_sql('qrcodeprod.json', 'qrcodeprod.sql')

if __name__ == "__main__":
    main()