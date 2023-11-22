import json
import asyncio
import os
import platform
import websockets
from Backend.db import MongoManager
import inspect
import logging
import ssl
logging.basicConfig(filename="./Data/logs.log", level=logging.DEBUG)

mongo_manager = MongoManager()

if platform.system() == "Linux" and os.path.exists("./Data/fullchain.pem"):
    # Load the Let's Encrypt certificate and private key
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain("./Data/fullchain.pem", "./Data/privkey.pem")

mongo_manager = MongoManager()

class Client:
    def __init__(self, routes, uid) -> None:
        self.websockets = []
        self.routes: str = routes
        self.uid: str = uid
        self.connections = []

    async def send_message(self, type, data=None,filter=None, **kwargs):
        json_data = {"type": type}
        if data:
            json_data = {**json_data, **data}
        if kwargs:
            json_data = {**json_data, **kwargs}

        string_formated_message = json.dumps(json_data)
        
        

class Client_Assistant(Client):
    def __init__(self, routes, uid) -> None:
        super().__init__(routes, uid)
        self.messages = []
        

    async def handle_connection(self, websocket, user_agent, headers):
        await super().handle_connection(websocket, user_agent, headers)
            
            
            

class Server:
    def __init__(self) -> None:
        self.routes = {}
        self.clients = {}

    def route(self, name=None):
        def registrar(func, name=name):
            async def new_func(*args, **kwargs):
                
                await func()
            
            name = name or func.__name__
            
            params = []
            
            for param in inspect.signature(func).parameters.values():
                if param.kind == param.POSITIONAL_ONLY:
                    raise Exception("Cannot have positional arguments")
                elif param.kind == param.VAR_POSITIONAL:
                    raise Exception("Cannot have positional arguments")
                elif param.kind != param.VAR_KEYWORD:
                    params.append(param.name)
            
            if len(params) == 0:
                raise Exception("Missing client as first parameter")
            
            
            self.routes[name] = func

            return new_func

        return registrar
