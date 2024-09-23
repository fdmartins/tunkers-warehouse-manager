import sys
import os

class FileRef:

    # Função para ajustar o caminho para o banco de dados
    @staticmethod
    def get_path(relative_path):
        """Retorna a URI para o banco de dados SQLite com o caminho correto."""
        if getattr(sys, 'frozen', False):
            # Se o programa estiver rodando como um executável empacotado
            base_path = sys._MEIPASS
        else:
            # Se o programa estiver rodando como um script Python
            base_path = os.path.abspath(".")
        
        # Caminho completo para o banco de dados SQLite
        db_path = os.path.join(base_path, relative_path)
        #print("local db: " + db_path)
        return f"{db_path}"