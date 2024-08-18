import ssl
from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='/certs/cert.pem', keyfile='/certs/key.pem')
    
    args = [
        'daphne', '-b', '0.0.0.0', '-p', '8000', 
        '--access-log', '-', '--proxy-headers', 
        'chat.asgi:application'
    ]
    
    daphne_server = CommandLineInterface(args)
    daphne_server.run()
