import webbrowser
import socket
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import logging
import time
import core
from logging.handlers import TimedRotatingFileHandler

port = 8080
DEBUG = False
VERSION = "20241015"

# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

# Function to open the default browser
def open_browser(ip, port):
    ip = '127.0.0.1'
    webbrowser.open(f'http://{ip}:{port}')

# Function to handle window close with confirmation
def on_closing(window):
    if messagebox.askokcancel("Fechar", "Confirma sua ação? Os LGVs pararão de receber missões!"):
        logging.info(">>>>>> ENCERRAMENTO CONFIRMADO PELO OPERADOR <<<<<<<")
        window.destroy()

# Function to create the tkinter window
def create_window(ip, port):
    window = tk.Tk()


    # Definindo o estilo das fontes
    font_style1 = ("Helvetica", 10)
    font_style2 = ("Helvetica", 13, "bold")
    font_style3 = ("Helvetica", 16, "bold")

    window.title("Não feche esta janela")

    # Definindo o tamanho da janela
    window.geometry('400x250')

    # Adicionando uma cor de fundo para a janela
    window.configure(bg='#f0f0f0')  # Cor de fundo suave

    # Criando um frame centralizado
    frame = tk.Frame(window, bg='#f0f0f0')
    frame.pack(pady=20)

    # Label do título principal
    label = tk.Label(frame, text="Sistema de Gestão de Posições", font=font_style3, bg='#f0f0f0', fg='#333333')
    label.pack(pady=10)

    # Label da versão
    label = tk.Label(frame, text=f"Versão: {VERSION}", font=font_style1, bg='#f0f0f0', fg='#666666')
    label.pack(pady=5)

    # Label do endereço IP e porta
    label = tk.Label(frame, text=f"Endereço: http://{ip}:{port}", font=font_style2, bg='#f0f0f0', fg='#007acc')
    label.pack(pady=10)

    # Botão para abrir o navegador
    button = tk.Button(frame, text="Abrir Tela/Browser", height=2, command=lambda: open_browser(ip, port),  font=font_style2)
    button.pack(pady=10) 

    # Override the close button event to ask for confirmation
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    

    window.mainloop()


# Flask thread for running the server
def run_flask():
    if DEBUG:
        core.app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    else:
        # For deploying an application to production, one option is to use Waitress, a production WSGI server.
        from waitress import serve
        serve(core.app, host='0.0.0.0', port=port)

if __name__ == '__main__':

    # Configuração  do logger
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format=('%(asctime)-20s | %(name)-30s | %(levelname)-8s | %(message)-50s'),
        handlers=[
            TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=15),  # Gera um arquivo por dia, mantem apenas os 15  dias.
            logging.StreamHandler()  # Envia as mensagens para o console
        ]
    )

    logging.info("===================================")
    logging.info("===================================")
    logging.info("          INICIADO SISTEMA         ")
    logging.info("===================================")
    logging.info("===================================")
        
    # capturando ip local.
    ip = get_local_ip()
    logging.info(f"IP da maquina server {ip}")
    
    # inicia servidor web
    logging.info(f"Iniciando Servidor Web")
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    core.start()

    #while True:
    #    time.sleep(1)
    if True:
        # Open browser automatically
        logging.info(f"Abrindo Browser Automaticamente...")
        #open_browser(ip, port)
        logging.info(f"Browser Aberto!")
        
        # Create the tkinter window
        logging.info(f"Criando Janela Local do Sistema...")
        create_window(ip, port)

        # janela prende aplicacao até o encerramento.
        
        logging.info(">>>>>> SISTEMA ENCERRADO <<<<<<<")