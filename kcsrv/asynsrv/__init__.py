from .srv import Server

server = Server()

def get():
    return server

def config(config_dict: dict = {}):
    server.config(config_dict)

def start():
    server.start()

def stop():
    server.stop()