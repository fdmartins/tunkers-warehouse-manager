from core import app

import webbrowser
import socket
import tkinter as tk
from tkinter import messagebox
from threading import Thread

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
        window.destroy()

# Function to create the tkinter window
def create_window(ip, port):
    window = tk.Tk()
    window.title("Não feche esta janela")

    label = tk.Label(window, text=f"Endereço IP: http://{ip}:{port}")
    label.pack(pady=10)

    button = tk.Button(window, text="Abrir Browser", command=lambda: open_browser(ip, port))
    button.pack(pady=10)

    window.geometry('300x100')

    # Override the close button event to ask for confirmation
    #window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    

    window.mainloop()


# Flask thread for running the server
def run_flask():
    if DEBUG:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    else:
        # For deploying an application to production, one option is to use Waitress, a production WSGI server.
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
        
    # Get the local IP and open the browser
    ip = get_local_ip()
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    
    # Open browser automatically
    #open_browser(ip, port)
    
    # Create the tkinter window
    create_window(ip, port)