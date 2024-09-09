import webbrowser
import socket
#import tkinter as tk
#from tkinter import messagebox
from threading import Thread
import logging
import time
import core


port = 8080
DEBUG = True


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
    webbrowser.open(f'http://{ip}:{port}')

# Function to handle window close with confirmation
def on_closing(window):
    if messagebox.askokcancel("Fechar", "Confirma sua ação? Os LGVs pararão de receber missões!"):
        logging.info(">>>>>> ENCERRAMENTO CONFIRMADO PELO OPERADOR <<<<<<<")
        window.destroy()

# Function to create the tkinter window
def create_window(ip, port):
    window = tk.Tk()
    window.title("Não feche esta janela")

    label = tk.Label(window, text=f"Sistema de Gestão Posições AGV")
    label.pack(pady=10)

    label = tk.Label(window, text=f"Endereço IP: http://{ip}:{port}")
    label.pack(pady=10)

    button = tk.Button(window, text="Abrir Browser", command=lambda: open_browser(ip, port))
    button.pack(pady=10)

    window.geometry('300x150')

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
        format=('%(asctime)-20s | %(name)-30s | %(levelname)-8s | %(message)-50s'),  # Formato do log
        handlers=[
            logging.FileHandler('app.log'),
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

    while True:
        time.sleep(1)
    if False:
        # Open browser automatically
        logging.info(f"Abrindo Browser Automaticamente...")
        #open_browser(ip, port)
        logging.info(f"Browser Aberto!")
        
        # Create the tkinter window
        logging.info(f"Criando Janela Local do Sistema...")
        create_window(ip, port)

        # janela prende aplicacao até o encerramento.
        
        logging.info(">>>>>> SISTEMA ENCERRADO <<<<<<<")