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


class Client:
    def __init__(self, routes, uid) -> None:
        self.websockets = []
        self.routes = routes
        self.uid = uid

    async def send_message(self, type, data=None, **kwargs):
        
        json_data = {"type": type}
        if data:
            json_data = {**json_data, **data}
        if kwargs:
            json_data = {**json_data, **kwargs}

        string_formated_message = json.dumps(json_data)
        for socket in self.websockets:
            logging.info(f"> {({key: str(value)[0:100] for key, value in json_data.items()})}")

            await socket.send(string_formated_message)
    
    async def wait_for_message(self, type):
        message_queue = asyncio.Queue()
        
        async def put_result_in_queue(client, **kwargs):

            await message_queue.put(kwargs)
        
        self.routes[type] = put_result_in_queue
        while True:
            message = await message_queue.get()
            del self.routes[type]
            return message
    
    async def handle_message(self, message):
        print(message)
        try:
            decoded_json_message = json.loads(message)
        except Exception as e:
            raise e

            await self.send_message("error")
            return
        
        logging.info(f"< {({key: str(value)[0:100] for key, value in decoded_json_message.items()})}")

        action = decoded_json_message.get("type")
        
        del decoded_json_message["type"]

        if not (action in self.routes and callable(self.routes.get(action))):
            await self.send_message("error", error="Not Callbable")
            return

        route = self.routes.get(action)

        message_keys = decoded_json_message.keys()
        
        route_arguments = []
        optional_arguments = []
        has_var_keyword= False
        
        for param in inspect.signature(route).parameters.values():
            if param.kind == param.VAR_KEYWORD:
                has_var_keyword = True
            else:
                route_arguments.append(param.name)
            
                if param.default != param.empty:
                    optional_arguments.append(param.name)

        if len(route_arguments) > 0:
            route_arguments = route_arguments[1:]

        arguments_to_provide = dict()

        for argument in route_arguments:
            if  (argument not in message_keys) and argument not in optional_arguments:
                await self.send_message(f"Missing argument {argument}")
                return
            elif (argument not in message_keys) and argument in optional_arguments:
                pass
            else:
                arguments_to_provide[argument] = decoded_json_message[argument]
                del decoded_json_message[argument]    
        if has_var_keyword:
            for key, value in decoded_json_message.items():
                arguments_to_provide[key] = value
                

        try:
            if inspect.iscoroutinefunction(route):
                task = asyncio.create_task(route(self, **arguments_to_provide))
            else:
                raise Exception("Route must be async")
        except Exception as e:
            await self.send_message("error", error=str(e))

    async def handle_connection(self, websocket):
        print(websocket)
        self.websockets.append(websocket)
        try:
            async for message in websocket:
                print(message)
                await self.handle_message(message)
        except Exception as e:
            print(e)
        self.websockets.remove(websocket)
        return


class Client_Assistant(Client):
    def __init__(self, routes, uid) -> None:
        super().__init__(routes, uid)
        self.messages = []


class Server:
    def __init__(self) -> None:
        self.routes = {}
        self.clients = {}

    def route(self, name=None):
        def registrar(func, name=name):
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

            return func

        return registrar

    async def websocket_server(self, websocket, path: str):
        print("hi")
        try:
            uid = websocket.request_headers.get("UID")
            print(uid)
            if not uid:
                async for message in websocket:
                    auth_message = message
                    break
                json_auth_message = json.loads(auth_message)
                uid = json_auth_message.get("UID")
                message_type = json_auth_message.get("type")
                print("hi")
                if not ((message_type == "Authentication") and (uid != None)):
                    await websocket.send("First message was not auth")
                    print("First message was not auth")

                    return
                
                if not uid in mongo_manager.get_valid_uids():
                    await websocket.send("Invalid UID")
                    print("InvalidUID")

                    return    
            
                
            if not uid in mongo_manager.get_valid_uids():
                await websocket.send("Invalid UID")
                print("Invalid UID")
                return
            else:
                if uid not in self.clients:
                    client = Client_Assistant(self.routes, uid)
                    self.clients[uid] = client
                    
                else:
                    client = self.clients[uid]
                print("handling")
                await client.handle_connection(websocket)

        except Exception as e:
            print(f"Exception occurred: {str(e)}")



    def serve(self):
        print("Sarted")
        if platform.system() == "Linux" and os.path.exists("./Data/fullchain.pem"):
            
            start_server = websockets.serve(self.websocket_server, "0.0.0.0", 8765, ssl=ssl_context)
        else:
            start_server = websockets.serve(self.websocket_server, "0.0.0.0", 8765)
            
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
