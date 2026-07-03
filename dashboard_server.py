import http.server
import socketserver
import os
import webbrowser

PORT = 8000
DIRECTORY = "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve the current directory
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Prevent caching for development/testing
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def iniciar_servidor():
    # Garantir que estamos na pasta correta
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = MyHTTPRequestHandler
    
    # Permitir reuso do endereço para evitar erro de porta em uso se reiniciado rápido
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n==================================================")
        print(f" Servidor do Dashboard rodando com sucesso!")
        print(f" Acesse em seu navegador: {url}")
        print(f" Para encerrar o servidor, pressione: CTRL + C")
        print(f"==================================================\n")
        
        # Abre automaticamente o navegador padrão do usuário no dashboard
        try:
            webbrowser.open(url)
        except Exception:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado pelo usuário.")

if __name__ == "__main__":
    iniciar_servidor()
